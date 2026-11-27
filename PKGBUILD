# Maintainer: Twilight0 <https://github.com/Twilight0>
pkgname=nouveau-utils
pkgver=2.3.0
pkgrel=1
pkgdesc="Userspace dynamic frequency governor, CLI management tool, and interactive TUI for Nouveau"
arch=('any')
url="https://github.com/Twilight0/nouveau-utils"
license=('GPL-2.0-only')
depends=('python')
optdepends=(
  'nouveau-dkms: out-of-tree dynamic reclocking DKMS module'
  'nouveau-cachyos-lts-v2: prebuilt reclocking module for linux-cachyos-lts-v2'
)
provides=('nouveau-utils')
backup=('etc/nouveau-dynclockd.conf')
source=(
  "nouveau-dynclockd.conf"
  "nouveau-dynclockd.py"
  "nouveau-dynclockd.service"
  "nouveau-ctrl"
  "nouveau-tui"
  "apps.conf.sample"
  "nouveau-recover"
  "nouveau-recover.service"
  "99-nouveau-recover.rules"
)
sha256sums=('cbe2d1ce8a7331e2cee2da2cc17afb8ec15b3164fdea5d068c42f0554b278081'
            '703330f767f5271beaf93a4527b74bdf26e185593fc2af96bcf69ae92aa9277d'
            '87f698b1de37689cb3889bfae916ceaba1caca634ab6a653b1602bda613b20e4'
            '37c33bc9254734c98f932caa8a52cd1d5fa10efe0ecc78c7fc71ca8ab3830029'
            '95a2209b11293df0380390984cd1d9b377523cbb907cdcb274a79dfed39e3453'
            'e5564d33b86b27af9cb46b2bfc26b4d09e222654f2f887522a2fa9426dae8fea'
            'e9c54d70907ccd95ab875f25fe5622879e4ca844594e8344c25504acb021c7d9'
            '63c8d6185a31cf5d31410cfd52e4b0d749e0f931bf3c042f8cc4b5d6f9912cba'
            '9c4bb66b5398365a88cbaf2856274b4c118b7859fdda1307b090223e6aa72946')

package() {
  # Configurations
  install -Dm644 "${srcdir}/nouveau-dynclockd.conf" "${pkgdir}/etc/nouveau-dynclockd.conf"
  install -d "${pkgdir}/etc/nouveau-dynclockd.d"
  install -Dm644 "${srcdir}/apps.conf.sample" "${pkgdir}/etc/nouveau-dynclockd.d/apps.conf.sample"

  # Systemd services & udev rules
  install -Dm644 "${srcdir}/nouveau-dynclockd.service" "${pkgdir}/usr/lib/systemd/system/nouveau-dynclockd.service"
  install -Dm644 "${srcdir}/nouveau-recover.service" "${pkgdir}/usr/lib/systemd/system/nouveau-recover.service"
  install -Dm644 "${srcdir}/99-nouveau-recover.rules" "${pkgdir}/usr/lib/udev/rules.d/99-nouveau-recover.rules"

  # Binaries
  install -Dm755 "${srcdir}/nouveau-ctrl" "${pkgdir}/usr/bin/nouveau-ctrl"
  install -Dm755 "${srcdir}/nouveau-tui" "${pkgdir}/usr/bin/nouveau-tui"
  install -Dm755 "${srcdir}/nouveau-dynclockd.py" "${pkgdir}/usr/bin/nouveau-dynclockd.py"
  install -Dm755 "${srcdir}/nouveau-recover" "${pkgdir}/usr/bin/nouveau-recover"
  ln -sf nouveau-dynclockd.py "${pkgdir}/usr/bin/nouveau-dynclockd"
}
