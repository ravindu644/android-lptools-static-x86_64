#!/bin/bash
set -euo pipefail

# Build static lptools binaries for Android
# Simple, robust build script

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SOURCE_DIR="${SCRIPT_DIR}/android-tools-35.0.2"
readonly BUILD_DIR="${SCRIPT_DIR}/build-static"
readonly DEPS_DIR="${SCRIPT_DIR}/static-deps"
readonly INSTALL_DIR="${SCRIPT_DIR}/static-binaries"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# Check dependencies
check_deps() {
    log_info "Checking dependencies..."
    local missing=()
    for cmd in cmake gcc g++ make go perl git wget tar strip; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing+=("$cmd")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing: ${missing[*]}"
        exit 1
    fi
    
    if ! rpm -q glibc-static libstdc++-static >/dev/null 2>&1; then
        log_warn "glibc-static or libstdc++-static not installed"
        log_info "Install with: sudo dnf install glibc-static libstdc++-static"
    fi
}

# Build static protobuf
build_protobuf() {
    local version="3.19.6"
    local protobuf_dir="${DEPS_DIR}/protobuf-${version}"
    local install_dir="${DEPS_DIR}/protobuf"
    local archive="${DEPS_DIR}/protobuf-cpp-${version}.tar.gz"
    local url="https://github.com/protocolbuffers/protobuf/releases/download/v${version}/protobuf-cpp-${version}.tar.gz"
    
    if [ -f "${install_dir}/lib/libprotobuf.a" ]; then
        log_info "Protobuf already built"
        return 0
    fi
    
    log_info "Building static protobuf ${version}..."
    mkdir -p "${DEPS_DIR}"
    cd "${DEPS_DIR}"
    
    # Download
    if [ ! -f "$archive" ]; then
        log_info "Downloading protobuf..."
        wget -q "$url" -O "$archive" || {
            log_error "Download failed"
            return 1
        }
    fi
    
    # Extract
    if [ ! -d "$protobuf_dir" ]; then
        log_info "Extracting protobuf..."
        tar -xzf "$archive" || {
            log_error "Extraction failed"
            return 1
        }
    fi
    
    cd "$protobuf_dir"
    
    # Build with autotools
    if [ ! -f "configure" ]; then
        log_info "Running autogen.sh..."
        ./autogen.sh >/dev/null 2>&1 || {
            log_error "autogen.sh failed"
            return 1
        }
    fi
    
    log_info "Configuring protobuf..."
    ./configure \
        --prefix="${install_dir}" \
        --disable-shared \
        --enable-static \
        --disable-dependency-tracking \
        CXXFLAGS="-O2 -fPIC" \
        CFLAGS="-O2 -fPIC" >configure.log 2>&1 || {
        log_error "Configure failed. Check configure.log"
        return 1
    }
    
    log_info "Building protobuf..."
    make -j$(nproc) >build.log 2>&1 || {
        log_error "Build failed. Check build.log"
        return 1
    }
    
    log_info "Installing protobuf..."
    make install >install.log 2>&1 || {
        log_error "Install failed. Check install.log"
        return 1
    }
    
    # Create CMake config files
    log_info "Creating CMake config..."
    mkdir -p "${install_dir}/lib/cmake/protobuf"
    cat > "${install_dir}/lib/cmake/protobuf/protobuf-targets.cmake" <<'EOF'
set(protobuf_LIBRARIES "@PROTOBUF_LIB@")
set(protobuf_INCLUDE_DIRS "@PROTOBUF_INCLUDE@")

if(NOT TARGET protobuf::libprotobuf)
    add_library(protobuf::libprotobuf STATIC IMPORTED)
    set_target_properties(protobuf::libprotobuf PROPERTIES
        IMPORTED_LOCATION "@PROTOBUF_LIB@"
        INTERFACE_INCLUDE_DIRECTORIES "@PROTOBUF_INCLUDE@"
    )
endif()
EOF
    sed -i "s|@PROTOBUF_LIB@|${install_dir}/lib/libprotobuf.a|g" \
        "${install_dir}/lib/cmake/protobuf/protobuf-targets.cmake"
    sed -i "s|@PROTOBUF_INCLUDE@|${install_dir}/include|g" \
        "${install_dir}/lib/cmake/protobuf/protobuf-targets.cmake"
    
    cat > "${install_dir}/lib/cmake/protobuf/protobuf-config.cmake" <<EOF
include("\${CMAKE_CURRENT_LIST_DIR}/protobuf-targets.cmake")
set(Protobuf_FOUND TRUE)
set(Protobuf_LIBRARIES protobuf::libprotobuf)
set(Protobuf_INCLUDE_DIRS "${install_dir}/include")
set(Protobuf_LIBRARY "${install_dir}/lib/libprotobuf.a")
EOF
    
    log_info "Protobuf built successfully"
}

# Main build
main() {
    log_info "=========================================="
    log_info "Building static lptools binaries"
    log_info "=========================================="
    
    if [ ! -d "$SOURCE_DIR" ]; then
        log_error "Source directory not found: $SOURCE_DIR"
        exit 1
    fi
    
    check_deps
    
    mkdir -p "$BUILD_DIR" "$DEPS_DIR" "$INSTALL_DIR"
    
    # Build protobuf
    build_protobuf
    
    # Clean build directory
    log_info "Cleaning build directory..."
    rm -rf "$BUILD_DIR"/*
    
    cd "$BUILD_DIR"
    
    # Configure CMake
    log_info "Configuring CMake..."
    export GO111MODULE=off
    export CMAKE_PREFIX_PATH="${DEPS_DIR}/protobuf/lib/cmake:${DEPS_DIR}/protobuf"
    
    local static_flags="-static"
    if rpm -q libstdc++-static >/dev/null 2>&1; then
        static_flags="${static_flags} -static-libstdc++"
    fi
    
    cmake "$SOURCE_DIR" \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=OFF \
        -DCMAKE_EXE_LINKER_FLAGS="${static_flags}" \
        -DCMAKE_C_FLAGS="-O2" \
        -DCMAKE_CXX_FLAGS="-O2" \
        -DCMAKE_FIND_LIBRARY_SUFFIXES=".a" \
        -DProtobuf_ROOT="${DEPS_DIR}/protobuf" \
        -DANDROID_TOOLS_USE_BUNDLED_FMT=ON \
        -DANDROID_TOOLS_USE_BUNDLED_LIBUSB=ON \
        -DANDROID_TOOLS_LIBUSB_ENABLE_UDEV=OFF \
        >cmake.log 2>&1
    
    if [ $? -ne 0 ]; then
        log_error "CMake configuration failed. Check cmake.log"
        tail -30 cmake.log | sed 's/^/  /'
        exit 1
    fi
    
    log_info "CMake configured successfully"
    
    # Build
    log_info "Building lptools..."
    cmake --build . --target lpadd lpdump lpflash lpmake lpunpack -j$(nproc) >build.log 2>&1 || {
        log_error "Build failed. Check build.log"
        tail -50 build.log | sed 's/^/  /'
        exit 1
    }
    
    log_info "Build completed"
    
    # Copy and strip binaries
    log_info "Installing binaries..."
    local binaries=("lpadd" "lpdump" "lpflash" "lpmake" "lpunpack")
    local all_ok=true
    
    for bin in "${binaries[@]}"; do
        local src="${BUILD_DIR}/vendor/${bin}"
        [ -f "$src" ] || src="${BUILD_DIR}/${bin}"
        
        if [ -f "$src" ]; then
            cp "$src" "$INSTALL_DIR/"
            
            if command -v strip >/dev/null 2>&1; then
                strip "$INSTALL_DIR/$bin" 2>/dev/null || true
            fi
            
            # Verify static linking
            local ldd_output=$(ldd "$INSTALL_DIR/$bin" 2>&1)
            if echo "$ldd_output" | grep -q "not a dynamic executable"; then
                log_info "$bin: ✓ Fully static"
            else
                local deps=$(echo "$ldd_output" | grep -v "linux-vdso" | awk '{print $1}' | grep -v "^$" || true)
                if [ -n "$deps" ]; then
                    log_warn "$bin: Has dynamic dependencies:"
                    echo "$deps" | sed 's/^/  - /'
                else
                    log_info "$bin: ✓ Fully static"
                fi
            fi
            
            ls -lh "$INSTALL_DIR/$bin" | awk '{print "  " $9 " (" $5 ")"}'
        else
            log_error "$bin: Not found!"
            all_ok=false
        fi
    done
    
    if [ "$all_ok" = true ]; then
        log_info "=========================================="
        log_info "Build complete! Binaries in: $INSTALL_DIR"
        log_info "=========================================="
    else
        log_error "Build incomplete!"
        exit 1
    fi
}

main "$@"
