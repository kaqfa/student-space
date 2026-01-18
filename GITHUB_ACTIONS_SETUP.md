# GitHub Actions Setup - Auto Deploy ke Domainesia

Dokumentasi lengkap untuk setup GitHub Actions agar bisa auto deploy ke Domainesia CloudHost setelah tests pass.

## 📋 Overview

GitHub Actions workflow ini akan:
1. ✅ **Run tests** dengan pytest menggunakan PostgreSQL 12
2. 🚀 **Auto deploy** ke Domainesia jika tests pass (hanya untuk push ke branch `main`/`master`)
3. 🔄 **Restart Passenger** setelah deployment

## 🔧 Setup GitHub Repository Secrets

Anda perlu menambahkan secrets di GitHub repository untuk koneksi SSH ke Domainesia.

### Langkah-langkah:

1. Buka repository GitHub Anda
2. Klik **Settings** > **Secrets and variables** > **Actions**
3. Klik **New repository secret**
4. Tambahkan secrets berikut:

### Required Secrets:

| Secret Name | Deskripsi | Contoh Value |
|------------|-----------|--------------|
| `SSH_HOST` | Hostname/IP server Domainesia | `srv123.niagahoster.com` atau IP address |
| `SSH_USERNAME` | Username SSH (biasanya sama dengan cPanel username) | `u123456` atau `username` |
| `SSH_PASSWORD` | Password SSH/cPanel | `your-password-here` |
| `SSH_PORT` | Port SSH (default: 22, tapi bisa beda) | `22` atau port custom |
| `PROJECT_PATH` | Path lengkap ke direktori proyek di server | `/home/username/banksoal` |

### Cara Mendapatkan Informasi SSH dari Domainesia:

#### 1. SSH Host
- Login ke cPanel Domainesia
- Lihat di bagian **General Information** atau **Server Information**
- Biasanya format: `srv123.niagahoster.com` atau IP address

#### 2. SSH Username & Password
- Username: sama dengan username cPanel Anda
- Password: sama dengan password cPanel Anda
- Atau bisa buat SSH key terpisah dari cPanel > **SSH Access**

#### 3. SSH Port
- Default: `22`
- Bisa dicek di cPanel > **SSH Access** > **Manage SSH Keys**
- Atau hubungi support Domainesia jika tidak yakin

#### 4. Project Path
- Path tempat Anda upload aplikasi Django
- Contoh: `/home/username/banksoal`
- Atau: `/home/username/public_html/banksoal`
- Pastikan path ini sudah ada dan berisi project Django Anda

### Screenshot: Cara Menambahkan Secrets

```
GitHub Repo → Settings → Secrets and variables → Actions → New repository secret

Name: SSH_HOST
Secret: srv123.niagahoster.com

[Add secret]
```

Ulangi untuk semua 5 secrets yang diperlukan.

## 📝 Persiapan di Server Domainesia

Sebelum GitHub Actions bisa auto deploy, pastikan hal-hal berikut sudah di-setup di server:

### 1. Project Sudah Ter-install

```bash
# SSH ke server
ssh username@srv123.niagahoster.com

# Navigate ke home directory
cd ~

# Clone repository (first time only)
git clone https://github.com/yourusername/student-space.git banksoal
cd banksoal

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/production.txt

# Create .env file
cp .env.production.example .env
nano .env  # Edit dengan credentials yang benar

# PENTING: Pastikan .env berisi DJANGO_SETTINGS_MODULE=config.settings.production
# untuk menghindari error ModuleNotFoundError: No module named 'debug_toolbar'

# Initial setup
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 2. Setup Git Credentials

Agar GitHub Actions bisa pull code, setup Git credentials:

**Opsi A: Personal Access Token (Recommended)**

```bash
# Generate Personal Access Token di GitHub:
# GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
# Pilih scope: repo (Full control of private repositories)

# Setup git credential
git config --global credential.helper store
git pull  # Masukkan username dan token (bukan password)
```

**Opsi B: SSH Key (Lebih Aman)**

```bash
# Generate SSH key di server
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Tambahkan ke GitHub:
# GitHub → Settings → SSH and GPG keys → New SSH key
# Paste public key content

# Update git remote ke SSH
cd ~/banksoal
git remote set-url origin git@github.com:yourusername/student-space.git
```

### 3. Create tmp Directory untuk Passenger Restart

```bash
cd ~/banksoal
mkdir -p tmp
```

### 4. Test Manual Deployment

Test semua command yang akan dijalankan GitHub Actions:

```bash
cd ~/banksoal
source venv/bin/activate
git pull origin main
pip install -r requirements/production.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

Jika semua berhasil tanpa error, GitHub Actions akan bisa auto deploy.

## 🚀 Cara Kerja Workflow

### Workflow File: `.github/workflows/deploy.yml`

Workflow ini punya 2 jobs:

#### Job 1: Test
- Trigger: Setiap push atau pull request ke branch `main`/`master`
- Setup PostgreSQL 12 untuk testing
- Install dependencies dari `requirements/development.txt`
- Run pytest dengan coverage report
- **Deploy hanya jalan jika test PASS**

#### Job 2: Deploy
- Trigger: Hanya untuk push ke `main`/`master` (tidak untuk PR)
- Hanya jalan jika job Test berhasil
- SSH ke server Domainesia
- Pull latest code
- Install/update dependencies
- Run migrations
- Collect static files
- Restart Passenger dengan `touch tmp/restart.txt`

## 📊 Monitoring Deployment

### Cara Melihat Status Deployment:

1. Buka repository GitHub
2. Klik tab **Actions**
3. Lihat workflow runs terbaru
4. Klik untuk melihat detail logs

### Status Indicators:

- ✅ **Green checkmark**: Tests pass & deployment sukses
- ❌ **Red X**: Tests failed atau deployment error
- 🟡 **Yellow dot**: Sedang running

### Troubleshooting Deployment Failures:

1. Klik workflow yang failed
2. Klik job yang error (Test atau Deploy)
3. Expand step yang failed untuk lihat error message

Common issues:
- **SSH connection failed**: Cek secrets SSH_HOST, SSH_USERNAME, SSH_PASSWORD
- **Git pull failed**: Cek git credentials di server
- **Migration failed**: Cek database credentials di .env
- **Permission denied**: Cek file permissions di server
- **ModuleNotFoundError: No module named 'debug_toolbar'**:
  - Pastikan .env berisi `DJANGO_SETTINGS_MODULE=config.settings.production`
  - Atau export DJANGO_SETTINGS_MODULE=config.settings.production sebelum run migrations
  - Install dari requirements/production.txt, BUKAN development.txt

## 🔐 Security Best Practices

### 1. Jangan Commit .env File
Pastikan `.env` ada di `.gitignore`:
```bash
# Check .gitignore
cat .gitignore | grep .env
```

### 2. Rotate SSH Password Regularly
Ganti password SSH dan update GitHub secrets secara berkala.

### 3. Gunakan SSH Keys (Lebih Aman)
Untuk production yang serius, gunakan SSH keys daripada password.

Update workflow untuk SSH key:

```yaml
- name: Deploy via SSH (with key)
  uses: appleboy/ssh-action@v1.0.3
  with:
    host: ${{ secrets.SSH_HOST }}
    username: ${{ secrets.SSH_USERNAME }}
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    port: ${{ secrets.SSH_PORT }}
    script: |
      # deployment commands...
```

Tambahkan secret `SSH_PRIVATE_KEY` berisi private key content.

### 4. Limit Branch yang Bisa Deploy
Workflow sudah di-set hanya deploy dari `main`/`master`. Jangan ubah ini kecuali perlu.

## 🧪 Testing Workflow

### Test di Branch Lain (Without Deploy):

```bash
# Buat branch baru
git checkout -b test-ci

# Commit changes
git add .
git commit -m "Test CI workflow"

# Push
git push origin test-ci

# Create Pull Request di GitHub
# Workflow akan run tests tapi TIDAK deploy
```

### Deploy ke Production:

```bash
# Merge ke main
git checkout main
git merge test-ci
git push origin main

# Workflow akan run tests DAN deploy jika pass
```

## 📋 Maintenance

### Update Workflow

Jika perlu update workflow (misal tambah step baru):

1. Edit `.github/workflows/deploy.yml`
2. Commit dan push
3. Workflow akan otomatis menggunakan versi terbaru

### Disable Auto Deploy Temporarily

Jika butuh disable auto deploy sementara:

**Opsi 1: Comment out deploy job**
```yaml
# deploy:
#   name: Deploy to Domainesia
#   runs-on: ubuntu-latest
#   ...
```

**Opsi 2: Disable workflow di GitHub**
- GitHub → Actions → Select workflow → Disable workflow

### Manual Deploy via SSH

Jika auto deploy error, bisa manual deploy:

```bash
ssh username@srv123.niagahoster.com
cd ~/banksoal
source venv/bin/activate

# Set production settings
export DJANGO_SETTINGS_MODULE=config.settings.production

git pull origin main
pip install -r requirements/production.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

## 📞 Support

Jika ada masalah:

1. **Check workflow logs** di GitHub Actions tab
2. **Check server logs** via SSH:
   ```bash
   tail -f ~/logs/error_log
   tail -f ~/banksoal/logs/django.log
   ```
3. **Hubungi support Domainesia** untuk masalah SSH/server
4. **Create issue** di repository GitHub untuk masalah workflow

## 🎯 Checklist Setup

Gunakan checklist ini untuk memastikan semua sudah di-setup:

- [ ] Repository sudah di-push ke GitHub
- [ ] Project sudah ter-install di server Domainesia
- [ ] Virtual environment sudah dibuat
- [ ] File `.env` sudah di-setup dengan credentials benar
- [ ] Git credentials di server sudah di-setup (PAT atau SSH key)
- [ ] Directory `tmp/` sudah dibuat untuk Passenger restart
- [ ] Manual deployment test sudah berhasil
- [ ] GitHub secrets sudah ditambahkan:
  - [ ] SSH_HOST
  - [ ] SSH_USERNAME
  - [ ] SSH_PASSWORD
  - [ ] SSH_PORT
  - [ ] PROJECT_PATH
- [ ] Test workflow dengan create PR
- [ ] Test deployment dengan push ke main

Jika semua checklist ✅, GitHub Actions siap digunakan! 🎉
