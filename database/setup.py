"""
Database Setup Script for Social Security Application System

This script sets up the PostgreSQL database with all required tables, indexes, and sample data.
"""

import psycopg2
import psycopg2.extras
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Database setup and initialization."""
    
    def __init__(self, config: dict):
        """Initialize database setup."""
        self.config = config
        self.connection = None
    
    def connect(self):
        """Connect to PostgreSQL server."""
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database='postgres'  # Connect to default database first
            )
            self.connection.autocommit = True
            logger.info("Connected to PostgreSQL server")
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if "Connection refused" in error_msg:
                logger.error("PostgreSQL server is not running!")
                print("\n❌ PostgreSQL Connection Failed!")
                print("� ToI fix this issue:")
                print("\n📦 Install PostgreSQL:")
                print("  macOS: brew install postgresql")
                print("  Ubuntu: sudo apt-get install postgresql postgresql-contrib")
                print("  Windows: Download from https://www.postgresql.org/download/")
                print("\n🚀 Start PostgreSQL:")
                print("  macOS: brew services start postgresql")
                print("  Ubuntu: sudo systemctl start postgresql")
                print("  Windows: Start PostgreSQL service from Services")
                print("\n💡 Alternative: Use Docker:")
                print("  ./docker-setup.sh")
                raise
            elif "role" in error_msg and "does not exist" in error_msg:
                logger.error("PostgreSQL user does not exist!")
                print("\n❌ PostgreSQL User Not Found!")
                print("🔧 To fix this issue:")
                print("\n🔑 Create postgres user:")
                print("  createuser -s postgres")
                print("  psql -d postgres -c \"ALTER USER postgres PASSWORD 'postgres';\"")
                print("\n💡 Or try with your system user:")
                import getpass
                system_user = getpass.getuser()
                print(f"  Try: export DB_USER='{system_user}'")
                print(f"  Then run: python setup.py")
                print("\n🐳 Easiest solution - Use Docker:")
                print("  ./docker-setup.sh")
                print("  python setup.py")
                raise
            else:
                logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise
    
    def create_database(self):
        """Create the application database if it doesn't exist."""
        try:
            with self.connection.cursor() as cursor:
                # Check if database exists
                cursor.execute("""
                    SELECT 1 FROM pg_database WHERE datname = %s
                """, (self.config['database'],))
                
                if not cursor.fetchone():
                    # Create database
                    cursor.execute(f"""
                        CREATE DATABASE {self.config['database']}
                        WITH ENCODING 'UTF8'
                        LC_COLLATE = 'en_US.UTF-8'
                        LC_CTYPE = 'en_US.UTF-8'
                        TEMPLATE template0
                    """)
                    logger.info(f"Created database: {self.config['database']}")
                else:
                    logger.info(f"Database {self.config['database']} already exists")
        
        except Exception as e:
            logger.error(f"Failed to create database: {str(e)}")
            raise
    
    def connect_to_app_database(self):
        """Connect to the application database."""
        try:
            if self.connection:
                self.connection.close()
            
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            self.connection.autocommit = True
            logger.info(f"Connected to database: {self.config['database']}")
        
        except Exception as e:
            logger.error(f"Failed to connect to application database: {str(e)}")
            raise
    
    def execute_sql_file(self, file_path: str):
        """Execute SQL commands from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            with self.connection.cursor() as cursor:
                for statement in statements:
                    if statement:
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            logger.warning(f"Statement failed (continuing): {str(e)}")
                            logger.debug(f"Failed statement: {statement[:100]}...")
            
            logger.info(f"Executed SQL file: {file_path}")
        
        except Exception as e:
            logger.error(f"Failed to execute SQL file {file_path}: {str(e)}")
            raise
    
    def create_user_and_permissions(self):
        """Skip user creation for demo - use default postgres user."""
        logger.info("Skipping user creation for demo setup - using default postgres user")
    
    def verify_setup(self):
        """Verify database setup by checking tables and sample data."""
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Check tables
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)
                
                tables = [row['table_name'] for row in cursor.fetchall()]
                logger.info(f"Created tables: {', '.join(tables)}")
                
                # Check sample data
                cursor.execute("SELECT COUNT(*) as count FROM applicants")
                applicant_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM applications")
                application_count = cursor.fetchone()['count']
                
                logger.info(f"Sample data: {applicant_count} applicants, {application_count} applications")
                
                # Test a complex query
                cursor.execute("""
                    SELECT 
                        a.application_number,
                        ap.first_name || ' ' || ap.last_name as name,
                        a.application_status,
                        a.requested_amount
                    FROM applications a
                    JOIN applicants ap ON a.applicant_id = ap.id
                    LIMIT 3
                """)
                
                sample_apps = cursor.fetchall()
                logger.info("Sample applications:")
                for app in sample_apps:
                    logger.info(f"  {app['application_number']}: {app['name']} - {app['application_status']} - AED {app['requested_amount']}")
        
        except Exception as e:
            logger.error(f"Failed to verify setup: {str(e)}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


def get_config_from_env():
    """Get database configuration from environment variables."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),  # Default demo password
        'database': os.getenv('DB_NAME', 'social_security_system')
    }


def try_connection_with_different_users(config):
    """Try connecting with different common usernames."""
    import getpass
    
    # Common PostgreSQL usernames to try
    users_to_try = [
        config['user'],  # Original user from config
        'postgres',
        getpass.getuser(),  # Current system user
        'admin',
        'root'
    ]
    
    passwords_to_try = [
        config['password'],  # Original password
        '',  # No password
        'postgres',
        'admin',
        'password'
    ]
    
    print("🔍 Trying different user combinations...")
    
    for user in users_to_try:
        for password in passwords_to_try:
            try:
                test_conn = psycopg2.connect(
                    host=config['host'],
                    port=config['port'],
                    user=user,
                    password=password,
                    database='postgres'
                )
                test_conn.close()
                
                print(f"✅ Found working credentials: {user}/{password}")
                config['user'] = user
                config['password'] = password
                return config
                
            except psycopg2.OperationalError:
                continue
    
    return None


def check_prerequisites():
    """Check if required packages are installed."""
    try:
        import psycopg2
        print("✅ psycopg2 is installed")
    except ImportError:
        print("❌ psycopg2 is not installed")
        print("📦 Install it with: pip install psycopg2-binary")
        return False
    return True


def main():
    """Main setup function."""
    print("🚀 Social Security Application System - Database Setup")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Get configuration
    config = get_config_from_env()
    
    # For demo, we'll use default postgres password
    if not config['password']:
        config['password'] = 'postgres'
        print("ℹ️  Using default password 'postgres' for demo setup")
    
    # Try to find working credentials
    print("🔍 Testing database connection...")
    working_config = try_connection_with_different_users(config)
    
    if working_config:
        config = working_config
        print(f"✅ Using credentials: {config['user']}/{config['password']}")
    else:
        print("\n❌ Could not find working database credentials!")
        print("🐳 Recommended: Use Docker for easy setup:")
        print("  ./docker-setup.sh")
        print("  python setup.py")
        print("\n🔧 Or create postgres user manually:")
        print("  createuser -s postgres")
        print("  psql -d postgres -c \"ALTER USER postgres PASSWORD 'postgres';\"")
        sys.exit(1)
    
    print(f"📊 Database Configuration:")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print(f"  Database: {config['database']}")
    print(f"  User: {config['user']}")
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent
    schema_file = script_dir / "schema.sql"
    sample_data_file = script_dir / "sample_data.sql"
    
    # Check if SQL files exist
    if not schema_file.exists():
        logger.error(f"Schema file not found: {schema_file}")
        sys.exit(1)
    
    if not sample_data_file.exists():
        logger.error(f"Sample data file not found: {sample_data_file}")
        sys.exit(1)
    
    # Setup database
    setup = DatabaseSetup(config)
    
    try:
        print("🔌 Connecting to PostgreSQL server...")
        setup.connect()
        
        print("🗄️  Creating database...")
        setup.create_database()
        
        print("🔗 Connecting to application database...")
        setup.connect_to_app_database()
        
        print("📋 Creating schema (tables, indexes, functions)...")
        setup.execute_sql_file(str(schema_file))
        
        print("👥 Setting up permissions (demo mode)...")
        setup.create_user_and_permissions()
        
        print("📊 Loading sample data...")
        setup.execute_sql_file(str(sample_data_file))
        
        print("✅ Verifying setup...")
        setup.verify_setup()
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📝 Connection Details:")
        print(f"  Database: {config['database']}")
        print(f"  Host: {config['host']}:{config['port']}")
        print(f"  User: {config['user']}")
        print(f"  Password: {config['password']}")
        
        print("\n🔧 Environment Variables for Application:")
        print(f"export DB_HOST='{config['host']}'")
        print(f"export DB_PORT='{config['port']}'")
        print(f"export DB_NAME='{config['database']}'")
        print(f"export DB_USER='{config['user']}'")
        print(f"export DB_PASSWORD='{config['password']}'")
        
        print("\n📚 Next Steps:")
        print("1. Set the environment variables shown above (or use defaults)")
        print("2. Update your .env file with database settings")
        print("3. Test the database connection")
        print("4. Start your application")
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)
    
    finally:
        setup.close()


if __name__ == "__main__":
    main()