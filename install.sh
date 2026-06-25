#!/usr/bin/env bash
# NEKO HQ — tek komut kurulum + 'neko' kisayolu + baslatma
set -e

REPO_RAW="https://raw.githubusercontent.com/ahmethasmerdogan/neko-hq-terminal/main"
DEST="$HOME/.neko-hq"
mkdir -p "$DEST"

echo "🐾 NEKO HQ indiriliyor..."
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$REPO_RAW/neko_tui.py" -o "$DEST/neko_tui.py"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$DEST/neko_tui.py" "$REPO_RAW/neko_tui.py"
else
  echo "Hata: curl ya da wget gerekli."; exit 1
fi

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python
command -v "$PY" >/dev/null 2>&1 || { echo "Hata: Python 3 bulunamadi (python.org)."; exit 1; }

# 'neko' kisayolunu kabuk profillerine ekle (claude gibi tek kelime)
add_shortcut() {
  local rc="$1"
  [ -e "$rc" ] || return 0
  if ! grep -q "neko-hq-shortcut" "$rc" 2>/dev/null; then
    printf '\n# neko-hq-shortcut\nneko() { %s "%s/neko_tui.py" "$@"; }\n' "$PY" "$DEST" >> "$rc"
    echo "  + 'neko' komutu eklendi: $rc"
  fi
}
SH="$(basename "${SHELL:-bash}")"
PRIMARY="$HOME/.bashrc"; [ "$SH" = "zsh" ] && PRIMARY="$HOME/.zshrc"
touch "$PRIMARY"
add_shortcut "$PRIMARY"
[ "$PRIMARY" != "$HOME/.zshrc" ] && add_shortcut "$HOME/.zshrc"
[ "$PRIMARY" != "$HOME/.bashrc" ] && add_shortcut "$HOME/.bashrc"

# PATH'e dusen bir launcher da birak (yedek)
BIN="$HOME/.local/bin"; mkdir -p "$BIN"
printf '#!/usr/bin/env bash\nexec %s "%s/neko_tui.py" "$@"\n' "$PY" "$DEST" > "$BIN/neko"
chmod +x "$BIN/neko"

echo "✓ Kuruldu."
echo "  Bundan sonra YENI bir terminalde sadece:  neko"
echo "  (ya da hemen kullan:  source $PRIMARY  && neko )"
echo "Baslatiliyor..."
exec "$PY" "$DEST/neko_tui.py" </dev/tty
