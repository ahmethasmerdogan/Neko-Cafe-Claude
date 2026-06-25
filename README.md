# 🐾 NEKO HQ — terminalde Claude CLI kedi kafesi

Claude CLI (Claude Code) çalışırken her oturumu bir kedi olarak, **doğrudan
terminalde** (tarayıcı yok) sevimli bir piksel kafede gösterir. Soru sorunca /
araçlar çalışınca kediler yazar; sessizlikte uyurlar. İsim, renk ve şapka gibi
özelleştirmeler **arayüzden** yapılır (json düzenlemek yok).

![NEKO HQ önizleme](docs/preview.png)

Tek dosya, yalnızca Python standart kütüphanesi. **macOS / Linux / Warp** ve
truecolor (24-bit renk) destekli bir terminal gerekir.

---

## ⚡ Hızlı kurulum (tek komut)

```bash
curl -fsSL https://raw.githubusercontent.com/ahmethasmerdogan/neko-hq-terminal/main/install.sh | bash
```

Bu komut: dosyayı indirir, `neko` kısayol komutunu kabuk profiline ekler ve
kafeyi başlatır. Bundan sonra **yeni bir terminalde sadece `neko`** yazman yeter.

> Claude Code zaten açıksa, hook'ların devreye girmesi için bir kez yeniden
> başlat (ya da Claude içinde `/hooks`).

### Alternatif: dosyayı elle indir

```bash
mkdir -p ~/.neko-hq
curl -fsSL https://raw.githubusercontent.com/ahmethasmerdogan/neko-hq-terminal/main/neko_tui.py -o ~/.neko-hq/neko_tui.py
python3 ~/.neko-hq/neko_tui.py
```

### Alternatif: klonla

```bash
git clone https://github.com/ahmethasmerdogan/neko-hq-terminal.git
cd neko-hq-terminal
python3 neko_tui.py
```

## 🐈 `neko` kısayol komutu

`claude` gibi, terminale `neko` yazınca kafe açılır. `install.sh` bunu otomatik
ekler. Elle eklemek istersen:

```bash
# zsh (macOS varsayılanı):
echo 'neko() { python3 "$HOME/.neko-hq/neko_tui.py" "$@"; }' >> ~/.zshrc && source ~/.zshrc
# bash:
echo 'neko() { python3 "$HOME/.neko-hq/neko_tui.py" "$@"; }' >> ~/.bashrc && source ~/.bashrc
```

## 🖥️ Warp'ta kullanım (önerilen)

1. Warp'ı aç. Paneli **alta** böl: `Cmd + Shift + D` (sağa bölmek için `Cmd + D`).
   Geniş kafe için alt pane (tam genişlik) idealdir.
2. **Üst** panede `claude` çalıştır.
3. **Alt** panede `neko` (ya da `python3 ~/.neko-hq/neko_tui.py`).
4. Claude'a soru sor → alt paneldeki kediler canlanır. Birden çok `claude`
   paneli açarsan her biri ayrı bir kedi olur.

> Kafe geniştir (~200 sütun). Dar kalırsa "Terminali büyüt" yazısı çıkar (bug
> yapmaz) — pane'i genişlet veya fontu biraz küçült.
> Linux'ta da aynı kısayollar; olmazsa sağ tık → "Split pane".

## ⌨️ Kontroller (arayüzden özelleştirme)

Alt satırda gösterilir:

| Tuş | İşlev |
|-----|-------|
| `←` `→` | kediyi seç (seçili kedinin üstünde sarı ok çıkar) |
| `n` | seçili kediye **isim** ver (listede yerinde yaz, Enter onay, Esc iptal) |
| `c` | seçili kedinin **rengini** değiştir |
| `h` | seçili kedinin **şapkasını** değiştir |
| `q` | çık |

Şapkalar: Noel şapkası, fiyonk, parti şapkası, bere, taç, kep, çiçek, yok.
İsim/renk/şapka seçimlerin `~/.neko-hq/cats.json`'a sessizce kaydedilir (elle
düzenlemen gerekmez); bir sonraki açılışta korunur.

## 🔧 Nasıl çalışır

Claude Code'un **hooks** özelliği her olayda (prompt, araç öncesi, bitiş) küçük
bir komutla `~/.neko-hq/activity.log`'a `session_id` ile satır yazar. Terminal
uygulaması bu dosyayı doğrudan okur: her oturum bir kedi olur, son araç kedinin
pozunu belirler (yazma / okuma / terminal), hareket yoksa kedi uyur. Ekran
truecolor + yarım-blok (▀) karakterlerle çizilir — gerçek piksel grafik,
terminalin içinde.

## 🪝 Hook & diğer komutlar

```bash
neko --install-hooks     # sadece hook'ları kur
neko --uninstall-hooks   # hook'ları kaldır
neko --no-install        # hook kurmadan çalıştır
neko --demo              # sahte hareketle önizleme
```

(`neko` yerine `python3 ~/.neko-hq/neko_tui.py` da kullanabilirsin.)

## 🩹 Sorun giderme

- **Kediler hep uyuyor / kedi yok:** hook'lar yüklü değil. `/hooks` ile bak,
  Claude Code'u yeniden başlat. Log'u izle: `tail -f ~/.neko-hq/activity.log`.
- **Renkler bozuk/kutucuklu:** terminal truecolor (24-bit) desteklemiyor. Warp
  destekler; bazı eski terminaller desteklemez.
- **"Terminali büyüt" yazısı:** pane çok küçük. Genişlet (~200 sütun) veya fontu
  küçült. Bu uyarı, görüntü bozulmasın diye vardır.
- **`neko` komutu bulunamadı:** yeni bir terminal aç ya da `source ~/.zshrc`
  (bash'te `~/.bashrc`).
- **Windows:** bu sürüm macOS/Linux içindir (raw terminal girişi). WSL'de çalışır.

## 🔒 Gizlilik

Hiçbir sunucu/ağ yok; her şey terminalde. Log ve ayarlar bilgisayarında
(`~/.neko-hq/`) kalır.

## 🧹 Kaldırma

```bash
neko --uninstall-hooks
rm -rf ~/.neko-hq
rm -f ~/.local/bin/neko
# ~/.zshrc / ~/.bashrc içindeki "# neko-hq-shortcut" satırlarını silebilirsin
```

## 📄 Lisans

MIT — bkz. `LICENSE`. İlham: PixelHQ, pixel-agents, claude-office.
