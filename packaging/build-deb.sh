#!/usr/bin/env bash
set -euo pipefail

VERSION="2.2.1"
PKGNAME="nouveau-utils"
ARCH="all"
DEB_NAME="${PKGNAME}_${VERSION}-1_${ARCH}.deb"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$(mktemp -d /tmp/deb_build.XXXXXX)"
trap 'rm -rf "$WORK_DIR"' EXIT

echo "[*] Building Debian package: ${DEB_NAME}"

# 1. Prepare data directory
DATA_DIR="${WORK_DIR}/data"
mkdir -p "${DATA_DIR}"

make -C "${REPO_ROOT}" install DESTDIR="${DATA_DIR}" PREFIX=/usr

# 2. Prepare control directory
CONTROL_DIR="${WORK_DIR}/control"
mkdir -p "${CONTROL_DIR}"

INSTALLED_SIZE=$(du -sk "${DATA_DIR}" | awk '{print $1}')

cat > "${CONTROL_DIR}/control" <<EOF
Package: ${PKGNAME}
Version: ${VERSION}-1
Architecture: ${ARCH}
Maintainer: Twilight0 <twilight0@vivaldi.net>
Installed-Size: ${INSTALLED_SIZE}
Depends: python3, nouveau-dkms
Suggests: python3-curses
Section: utils
Priority: optional
Homepage: https://github.com/Twilight0/nouveau-utils
Description: Userspace dynamic governor, CLI, and TUI for Nouveau
 Userspace dynamic frequency governor, command-line management tool,
 and interactive curses TUI for Nouveau GPU reclocking.
EOF

cp "${REPO_ROOT}/packaging/debian/nouveau-utils.postinst" "${CONTROL_DIR}/postinst"
cp "${REPO_ROOT}/packaging/debian/nouveau-utils.prerm" "${CONTROL_DIR}/prerm"
chmod 755 "${CONTROL_DIR}/postinst" "${CONTROL_DIR}/prerm"

# 3. Create debian-binary
echo "2.0" > "${WORK_DIR}/debian-binary"

# 4. Create control.tar.gz and data.tar.xz
tar --owner=0 --group=0 -czf "${WORK_DIR}/control.tar.gz" -C "${CONTROL_DIR}" .
tar --owner=0 --group=0 -cJf "${WORK_DIR}/data.tar.xz" -C "${DATA_DIR}" .

# 5. Pack deb
ar -rc "${REPO_ROOT}/${DEB_NAME}" "${WORK_DIR}/debian-binary" "${WORK_DIR}/control.tar.gz" "${WORK_DIR}/data.tar.xz"

echo "[✓] Built Debian package: ${REPO_ROOT}/${DEB_NAME}"
