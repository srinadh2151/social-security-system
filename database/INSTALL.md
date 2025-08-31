# Database Installation Guide

This guide helps you set up PostgreSQL for the Social Security Application System demo.

## 🚀 Quick Start Options

### Option 1: Docker (Recommended for Demo)

**Easiest way to get started:**

```bash
cd database
./docker-setup.sh
python setup.py
```

This will:
- ✅ Start PostgreSQL in Docker
- ✅ Set up with default credentials (postgres/postgres)
- ✅ No local installation needed

### Option 2: Local PostgreSQL Installation

#### macOS (using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Create default user (if needed)
createuser -s postgres
psql -U postgres -c "ALTER USER postgres PASSWORD 'postgres';"

# Run database setup
cd database
python setup.py
```

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Set up user
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"

# Run database setup
cd database
python setup.py
```

#### Windows
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install with default settings
3. Set password to 'postgres' during installation
4. Run database setup:
   ```cmd
   cd database
   python setup.py
   ```

## 🔧 Troubleshooting

### Connection Refused Error
```
connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
```

**Solutions:**
1. **Check if PostgreSQL is running:**
   ```bash
   # macOS
   brew services list | grep postgresql
   
   # Linux
   sudo systemctl status postgresql
   
   # Windows
   Check Services.msc for PostgreSQL service
   ```

2. **Start PostgreSQL:**
   ```bash
   # macOS
   brew services start postgresql
   
   # Linux
   sudo systemctl start postgresql
   
   # Docker
   ./docker-setup.sh
   ```

### Authentication Failed
```
FATAL: password authentication failed for user "postgres"
```

**Solutions:**
1. **Reset password:**
   ```bash
   # Local installation
   sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
   
   # Or use your actual password in .env file
   echo "DB_PASSWORD=your_actual_password" >> .env
   ```

2. **Use Docker (simpler):**
   ```bash
   ./docker-setup.sh
   ```

### Missing psycopg2
```
ModuleNotFoundError: No module named 'psycopg2'
```

**Solution:**
```bash
pip install psycopg2-binary
```

## 🐳 Docker Commands Reference

```bash
# Start PostgreSQL container
./docker-setup.sh

# Check if running
docker ps | grep postgres-demo

# Stop container
docker stop postgres-demo

# Start existing container
docker start postgres-demo

# Remove container (will lose data)
docker stop postgres-demo && docker rm postgres-demo

# Connect to PostgreSQL in container
docker exec -it postgres-demo psql -U postgres

# View logs
docker logs postgres-demo
```

## 📝 Environment Variables

Create a `.env` file in the project root:

```bash
# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social_security_system
DB_USER=postgres
DB_PASSWORD=postgres
```

## ✅ Verify Installation

After setup, you should see:

```
🎉 Database setup completed successfully!

📝 Connection Details:
  Database: social_security_system
  Host: localhost:5432
  User: postgres
  Password: postgres

Sample data: 5 applicants, 5 applications
```

## 🆘 Still Having Issues?

1. **Check PostgreSQL version:** `psql --version` (need 12+)
2. **Check port availability:** `lsof -i :5432` (should show postgres)
3. **Try Docker option:** Often simpler for demos
4. **Check firewall:** Make sure port 5432 is not blocked

## 🔄 Reset Database

To start fresh:

```bash
# Drop and recreate
psql -U postgres -c "DROP DATABASE IF EXISTS social_security_system;"
python setup.py

# Or with Docker
docker stop postgres-demo && docker rm postgres-demo
./docker-setup.sh
python setup.py
```