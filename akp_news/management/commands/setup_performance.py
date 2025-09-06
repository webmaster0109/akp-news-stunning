"""
Management command to set up database performance optimizations for Supabase PostgreSQL
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Set up performance optimizations for AKP News with Supabase PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-indexes',
            action='store_true',
            help='Create database indexes for better performance',
        )
        parser.add_argument(
            '--create-cache-table',
            action='store_true',
            help='Create database cache table',
        )
        parser.add_argument(
            '--analyze-tables',
            action='store_true',
            help='Analyze tables to update PostgreSQL statistics',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all performance optimizations',
        )

    def handle(self, *args, **options):
        """
        Set up all performance optimizations
        """
        if options['all']:
            options['create_indexes'] = True
            options['create_cache_table'] = True
            options['analyze_tables'] = True

        if options['create_cache_table']:
            self.create_cache_table()
            
        if options['create_indexes']:
            self.create_database_indexes()
            
        if options['analyze_tables']:
            self.analyze_tables()
        
        self.stdout.write(
            self.style.SUCCESS('Performance optimizations completed!')
        )

    def create_cache_table(self):
        """
        Create the database cache table
        """
        self.stdout.write("Creating database cache table...")
        
        try:
            from django.core.management import call_command
            call_command('createcachetable')
            self.stdout.write(
                self.style.SUCCESS('✓ Database cache table created successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating cache table: {e}')
            )

    def create_database_indexes(self):
        """
        Create optimized database indexes for AKP News
        """
        self.stdout.write("Creating database indexes...")
        
        indexes_to_create = [
            # News table indexes
            {
                'name': 'idx_news_published_active_date',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_news_published_active_date 
                    ON akp_news_news (is_published, is_active, published_at DESC)
                '''
            },
            {
                'name': 'idx_news_category_published',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_news_category_published 
                    ON akp_news_news (category_id, is_published, published_at DESC) 
                    WHERE is_active = true AND is_published = true
                '''
            },
            {
                'name': 'idx_news_slug_unique',
                'sql': '''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_news_slug_unique 
                    ON akp_news_news (slug) 
                    WHERE is_published = true
                '''
            },
            {
                'name': 'idx_news_author_published',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_news_author_published 
                    ON akp_news_news (author_id, published_at DESC) 
                    WHERE is_published = true AND is_active = true
                '''
            },
            
            # Category indexes
            {
                'name': 'idx_category_active_order',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_category_active_order 
                    ON akp_news_newscategory ("order", name) 
                    WHERE is_active = true
                '''
            },
            
            # Banner and advertisement indexes
            {
                'name': 'idx_news_banner_active_date',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_news_banner_active_date 
                    ON akp_news_newshomebanner (is_active, created_at DESC)
                '''
            },
            {
                'name': 'idx_advertisements_active_size',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_advertisements_active_size 
                    ON akp_news_advertisements (is_active, banner_size)
                '''
            },
            
            # Live updates index
            {
                'name': 'idx_live_updates_active_date',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_live_updates_active_date 
                    ON akp_news_liveupdates (is_active, created_at DESC)
                '''
            },
            
            # Web stories index
            {
                'name': 'idx_webstory_active_date',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_webstory_active_date 
                    ON webstories_webstory (is_active, created_at DESC)
                '''
            },
            
            # User and session indexes
            {
                'name': 'idx_user_email_active',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_user_email_active 
                    ON akp_accounts_customuser (email) 
                    WHERE is_active = true
                '''
            },
            
            # Full-text search indexes for PostgreSQL
            {
                'name': 'idx_news_title_gin',
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_news_title_gin 
                    ON akp_news_news 
                    USING gin(to_tsvector('english', title))
                '''
            },
            {
                'name': 'idx_news_content_gin', 
                'sql': '''
                    CREATE INDEX IF NOT EXISTS idx_news_content_gin 
                    ON akp_news_news 
                    USING gin(to_tsvector('english', content))
                '''
            },
        ]
        
        with connection.cursor() as cursor:
            created_count = 0
            failed_count = 0
            
            for index in indexes_to_create:
                try:
                    cursor.execute(index['sql'])
                    self.stdout.write(f"✓ Created index: {index['name']}")
                    created_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ Failed to create {index['name']}: {e}")
                    )
                    failed_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created {created_count} indexes, {failed_count} failed')
            )

    def analyze_tables(self):
        """
        Analyze tables to update PostgreSQL statistics for better query planning
        """
        self.stdout.write("Analyzing database tables...")
        
        tables_to_analyze = [
            'akp_news_news',
            'akp_news_newscategory', 
            'akp_news_newssubcategory',
            'akp_news_newstag',
            'akp_news_newshomebanner',
            'akp_news_advertisements',
            'akp_news_liveupdates',
            'akp_accounts_customuser',
            'webstories_webstory',
        ]
        
        with connection.cursor() as cursor:
            analyzed_count = 0
            
            for table in tables_to_analyze:
                try:
                    cursor.execute(f"ANALYZE {table}")
                    self.stdout.write(f"✓ Analyzed table: {table}")
                    analyzed_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ Failed to analyze {table}: {e}")
                    )
            
            # Global analyze
            try:
                cursor.execute("ANALYZE")
                self.stdout.write("✓ Global database analysis completed")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Global analysis failed: {e}")
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Analyzed {analyzed_count} tables')
            )
