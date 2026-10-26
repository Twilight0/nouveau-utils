# Maintainer: Twilight0 <https://github.com/Twilight0>
pkgname=nouveau-utils
pkgver=2.2.2
pkgrel=1
pkgdesc="Userspace dynamic frequency governor, CLI management tool, and interactive TUI for Nouveau"
arch=('any')
url="https://github.com/Twilight0/nouveau-utils"
license=('GPL-2.0-only')
depends=('python' 'nouveau-dkms')
provides=('nouveau-utils')
backup=('etc/nouveau-dynclockd.conf')
source=(
  "nouveau-dynclockd.conf"
  "nouveau-dynclockd.py"
  "nouveau-dynclockd.service"
  "nouveau-ctrl"
  "nouveau-tui"
  "apps.conf.sample"
)
sha256sums=('0bd9da376f1df0c1b4015de533bb71da6e2ba9ea333a1778ef590337e3d90492'
            '6accc66f39a3680036086aff948e011dcb10040c7cb4e46bfda002a52f8e4a54'
            '87f698b1de37689cb3889bfae916ceaba1caca634ab6a653b1602bda613b20e4'
            'd46e9f4796ffd5386fe1376a6f38205f6098f550636b9bc693d6bf6fc4496f9c'
            'a58f3aea24b5ed07bbebb744807b53585d0498c1e24f457b31127cb43459a158'
            'e5564d33b86b27af9cb46b2bfc26b4d09e222654f2f887522a2fa9426dae8fea')

package() {
  # Configurations
  install -Dm644 "${srcdir}/nouveau-dynclockd.conf" "${pkgdir}/etc/nouveau-dynclockd.conf"
  install -d "${pkgdir}/etc/nouveau-dynclockd.d"
  install -Dm644 "${srcdir}/apps.conf.sample" "${pkgdir}/etc/nouveau-dynclockd.d/apps.conf.sample"

  # Systemd service
  install -Dm644 "${srcdir}/nouveau-dynclockd.service" "${pkgdir}/usr/lib/systemd/system/nouveau-dynclockd.service"

  # Binaries
  install -Dm755 "${srcdir}/nouveau-ctrl" "${pkgdir}/usr/bin/nouveau-ctrl"
  install -Dm755 "${srcdir}/nouveau-tui" "${pkgdir}/usr/bin/nouveau-tui"
  install -Dm755 "${srcdir}/nouveau-dynclockd.py" "${pkgdir}/usr/bin/nouveau-dynclockd.py"
  ln -sf nouveau-dynclockd.py "${pkgdir}/usr/bin/nouveau-dynclockd"
}
