"""
Comprehensive Internship & Sector Seeding Script
Adds all major programming languages and worldwide internship opportunities
"""

import uuid
import sqlite3
from datetime import datetime
from database import execute_db, query_db

def seed_sectors():
    """Create all major sectors"""
    sectors = [
        {
            'name': 'Engineering & Technology',
            'slug': 'engineering-technology',
            'icon_url': 'code',
            'description': 'Software development, web development, mobile apps, cloud computing, AI/ML'
        },
        {
            'name': 'Data Science & Analytics',
            'slug': 'data-science-analytics',
            'icon_url': 'bar-chart-2',
            'description': 'Data analysis, business intelligence, statistical analysis, big data'
        },
        {
            'name': 'Cybersecurity',
            'slug': 'cybersecurity',
            'icon_url': 'shield',
            'description': 'Network security, ethical hacking, penetration testing, security infrastructure'
        },
        {
            'name': 'DevOps & Cloud',
            'slug': 'devops-cloud',
            'icon_url': 'cloud',
            'description': 'AWS, Azure, GCP, Kubernetes, Docker, CI/CD pipelines'
        },
        {
            'name': 'Frontend Development',
            'slug': 'frontend-development',
            'icon_url': 'monitor',
            'description': 'React, Vue, Angular, HTML/CSS, JavaScript, UI/UX'
        },
        {
            'name': 'Backend Development',
            'slug': 'backend-development',
            'icon_url': 'database',
            'description': 'Node.js, Django, Spring, FastAPI, databases, APIs'
        },
        {
            'name': 'Mobile App Development',
            'slug': 'mobile-app-development',
            'icon_url': 'smartphone',
            'description': 'iOS, Android, React Native, Flutter, cross-platform'
        },
        {
            'name': 'Artificial Intelligence & ML',
            'slug': 'ai-machine-learning',
            'icon_url': 'brain',
            'description': 'Machine learning, deep learning, NLP, computer vision, TensorFlow'
        },
        {
            'name': 'Blockchain & Web3',
            'slug': 'blockchain-web3',
            'icon_url': 'link-2',
            'description': 'Solidity, smart contracts, DeFi, cryptocurrencies, blockchain'
        },
        {
            'name': 'Game Development',
            'slug': 'game-development',
            'icon_url': 'gamepad-2',
            'description': 'Unity, Unreal Engine, game design, graphics programming'
        },
        {
            'name': 'Quality Assurance & Testing',
            'slug': 'qa-testing',
            'icon_url': 'check-circle',
            'description': 'Automation testing, manual testing, performance testing, QA'
        },
        {
            'name': 'Business & Management',
            'slug': 'business-management',
            'icon_url': 'briefcase',
            'description': 'Business analysis, project management, product management, strategy'
        },
        {
            'name': 'Marketing & Digital',
            'slug': 'marketing-digital',
            'icon_url': 'trending-up',
            'description': 'Digital marketing, SEO, content marketing, social media'
        },
        {
            'name': 'Finance & Banking',
            'slug': 'finance-banking',
            'icon_url': 'credit-card',
            'description': 'Fintech, financial analysis, trading, banking systems'
        },
        {
            'name': 'Design & UX/UI',
            'slug': 'design-ux-ui',
            'icon_url': 'palette',
            'description': 'UI/UX design, graphic design, interaction design, prototyping'
        }
    ]
    
    for sector in sectors:
        existing = query_db(
            "SELECT id FROM sectors WHERE slug = ?",
            (sector['slug'],),
            one=True
        )
        if not existing:
            sector_id = str(uuid.uuid4())
            execute_db(
                """INSERT INTO sectors (id, name, slug, icon_url, description)
                   VALUES (?, ?, ?, ?, ?)""",
                (sector_id, sector['name'], sector['slug'], sector['icon_url'], sector['description'])
            )
            print(f"✅ Created sector: {sector['name']}")
        else:
            print(f"⏭️  Sector already exists: {sector['name']}")

def seed_internships():
    """Create comprehensive internships for all sectors"""
    
    # Get all sectors
    sectors = query_db("SELECT id, name, slug FROM sectors")
    sector_map = {s['slug']: s['id'] for s in sectors}
    
    internships = [
        # PROGRAMMING LANGUAGES - Backend
        {
            'sector': 'backend-development',
            'title': 'Python Backend Development Internship',
            'slug': 'python-backend-dev',
            'description': 'Learn Django, FastAPI, Flask and build scalable backend services with Python',
            'duration': 4
        },
        {
            'sector': 'backend-development',
            'title': 'Java Enterprise Development Internship',
            'slug': 'java-enterprise-dev',
            'description': 'Master Spring Boot, Hibernate, and enterprise Java development patterns',
            'duration': 4
        },
        {
            'sector': 'backend-development',
            'title': 'C++ Systems Programming Internship',
            'slug': 'cpp-systems-programming',
            'description': 'Deep dive into C++ for systems programming, game engines, and performance-critical applications',
            'duration': 4
        },
        {
            'sector': 'backend-development',
            'title': 'Go Language Backend Development',
            'slug': 'go-backend-dev',
            'description': 'Build high-performance services with Go, microservices, and concurrent programming',
            'duration': 4
        },
        {
            'sector': 'backend-development',
            'title': 'Node.js & JavaScript Backend Internship',
            'slug': 'nodejs-backend-dev',
            'description': 'Express.js, NestJS, and full-stack JavaScript development',
            'duration': 4
        },
        {
            'sector': 'backend-development',
            'title': 'Rust Systems & Backend Development',
            'slug': 'rust-backend-dev',
            'description': 'Memory safety and performance with Rust, Actix-web, and Tokio',
            'duration': 4
        },
        {
            'sector': 'backend-development',
            'title': 'C# .NET Backend Development',
            'slug': 'csharp-dotnet-dev',
            'description': 'ASP.NET Core, Entity Framework, and Microsoft Azure cloud development',
            'duration': 4
        },
        {
            'sector': 'backend-development',
            'title': 'PHP & Laravel Web Development',
            'slug': 'php-laravel-dev',
            'description': 'Laravel framework, database design, and scalable web applications',
            'duration': 4
        },
        {
            'sector': 'backend-development',
            'title': 'Ruby on Rails Development Internship',
            'slug': 'ruby-rails-dev',
            'description': 'Rapid web development with Ruby on Rails and MVC architecture',
            'duration': 4
        },
        {
            'sector': 'backend-development',
            'title': 'Kotlin Backend & Android Development',
            'slug': 'kotlin-backend-dev',
            'description': 'Modern JVM language Kotlin for backend services and Android apps',
            'duration': 4
        },
        
        # FRONTEND DEVELOPMENT
        {
            'sector': 'frontend-development',
            'title': 'React.js Frontend Development Internship',
            'slug': 'react-frontend-dev',
            'description': 'Modern React development with hooks, state management, and component design',
            'duration': 4
        },
        {
            'sector': 'frontend-development',
            'title': 'Vue.js Frontend Development Internship',
            'slug': 'vue-frontend-dev',
            'description': 'Progressive Vue.js framework, composition API, and SPA development',
            'duration': 4
        },
        {
            'sector': 'frontend-development',
            'title': 'Angular Enterprise Frontend Development',
            'slug': 'angular-frontend-dev',
            'description': 'Enterprise-grade Angular applications, TypeScript, and RxJS',
            'duration': 4
        },
        {
            'sector': 'frontend-development',
            'title': 'TypeScript & Advanced JavaScript',
            'slug': 'typescript-javascript-dev',
            'description': 'Type-safe JavaScript, async programming, and modern ES6+ features',
            'duration': 4
        },
        {
            'sector': 'frontend-development',
            'title': 'Next.js & React Ecosystem Internship',
            'slug': 'nextjs-react-ecosystem',
            'description': 'SSR, static generation, API routes, and full-stack React applications',
            'duration': 4
        },
        {
            'sector': 'frontend-development',
            'title': 'Svelte & Modern Web Framework',
            'slug': 'svelte-web-framework',
            'description': 'Reactive web development with Svelte, build optimization, and animations',
            'duration': 4
        },
        
        # MOBILE DEVELOPMENT
        {
            'sector': 'mobile-app-development',
            'title': 'React Native Mobile Development',
            'slug': 'react-native-mobile',
            'description': 'Cross-platform iOS and Android development with React Native',
            'duration': 4
        },
        {
            'sector': 'mobile-app-development',
            'title': 'Flutter App Development Internship',
            'slug': 'flutter-mobile-dev',
            'description': 'Beautiful native apps with Flutter and Dart programming language',
            'duration': 4
        },
        {
            'sector': 'mobile-app-development',
            'title': 'iOS Native Development with Swift',
            'slug': 'ios-swift-dev',
            'description': 'Native iOS development, SwiftUI, and Apple ecosystem',
            'duration': 4
        },
        {
            'sector': 'mobile-app-development',
            'title': 'Android Native Development with Kotlin',
            'slug': 'android-kotlin-dev',
            'description': 'Native Android development, Jetpack, and Material Design',
            'duration': 4
        },
        
        # AI & MACHINE LEARNING
        {
            'sector': 'ai-machine-learning',
            'title': 'Python Machine Learning Internship',
            'slug': 'python-ml-internship',
            'description': 'TensorFlow, Keras, scikit-learn, and deep learning with Python',
            'duration': 4
        },
        {
            'sector': 'ai-machine-learning',
            'title': 'Deep Learning & Computer Vision',
            'slug': 'deep-learning-cv',
            'description': 'CNN, object detection, image segmentation, and computer vision projects',
            'duration': 4
        },
        {
            'sector': 'ai-machine-learning',
            'title': 'Natural Language Processing Internship',
            'slug': 'nlp-internship',
            'description': 'NLP, transformers, BERT, GPT models, and text analysis',
            'duration': 4
        },
        {
            'sector': 'ai-machine-learning',
            'title': 'Reinforcement Learning & RL Agents',
            'slug': 'reinforcement-learning',
            'description': 'Q-learning, policy gradients, game AI, and autonomous agents',
            'duration': 4
        },
        
        # DATA SCIENCE & ANALYTICS
        {
            'sector': 'data-science-analytics',
            'title': 'Data Analysis with Python Internship',
            'slug': 'data-analysis-python',
            'description': 'Pandas, NumPy, Matplotlib, and data visualization with Python',
            'duration': 4
        },
        {
            'sector': 'data-science-analytics',
            'title': 'Big Data & Apache Spark',
            'slug': 'big-data-spark',
            'description': 'Distributed computing, Hadoop, Spark, and large-scale data processing',
            'duration': 4
        },
        {
            'sector': 'data-science-analytics',
            'title': 'SQL Database & Data Engineering',
            'slug': 'sql-data-engineering',
            'description': 'Advanced SQL, database design, ETL pipelines, and data warehousing',
            'duration': 4
        },
        {
            'sector': 'data-science-analytics',
            'title': 'Business Intelligence & Analytics',
            'slug': 'bi-analytics',
            'description': 'Tableau, Power BI, data visualization, and business insights',
            'duration': 4
        },
        
        # DEVOPS & CLOUD
        {
            'sector': 'devops-cloud',
            'title': 'AWS Cloud Architecture Internship',
            'slug': 'aws-cloud-internship',
            'description': 'EC2, S3, Lambda, RDS, CloudFront, and AWS best practices',
            'duration': 4
        },
        {
            'sector': 'devops-cloud',
            'title': 'Microsoft Azure Cloud Development',
            'slug': 'azure-cloud-dev',
            'description': 'Azure services, Virtual Machines, App Services, and cloud infrastructure',
            'duration': 4
        },
        {
            'sector': 'devops-cloud',
            'title': 'Google Cloud Platform Internship',
            'slug': 'gcp-internship',
            'description': 'GCP services, BigQuery, Cloud Run, and Google Cloud infrastructure',
            'duration': 4
        },
        {
            'sector': 'devops-cloud',
            'title': 'Docker & Kubernetes Container Orchestration',
            'slug': 'docker-kubernetes',
            'description': 'Containerization, Kubernetes deployment, microservices architecture',
            'duration': 4
        },
        {
            'sector': 'devops-cloud',
            'title': 'CI/CD Pipeline & Jenkins Automation',
            'slug': 'cicd-jenkins',
            'description': 'Continuous integration, continuous deployment, automation tools',
            'duration': 4
        },
        {
            'sector': 'devops-cloud',
            'title': 'Infrastructure as Code (Terraform)',
            'slug': 'iac-terraform',
            'description': 'Terraform, CloudFormation, and infrastructure automation',
            'duration': 4
        },
        
        # CYBERSECURITY
        {
            'sector': 'cybersecurity',
            'title': 'Ethical Hacking & Penetration Testing',
            'slug': 'ethical-hacking-pentest',
            'description': 'Security testing, vulnerability assessment, and ethical hacking',
            'duration': 4
        },
        {
            'sector': 'cybersecurity',
            'title': 'Network Security Internship',
            'slug': 'network-security',
            'description': 'Firewalls, VPN, intrusion detection, and network hardening',
            'duration': 4
        },
        {
            'sector': 'cybersecurity',
            'title': 'Application Security & Secure Coding',
            'slug': 'app-security',
            'description': 'OWASP, secure coding, vulnerability prevention, and code review',
            'duration': 4
        },
        {
            'sector': 'cybersecurity',
            'title': 'Cloud Security & Compliance',
            'slug': 'cloud-security-compliance',
            'description': 'Cloud security, identity management, GDPR, and compliance',
            'duration': 4
        },
        
        # BLOCKCHAIN & WEB3
        {
            'sector': 'blockchain-web3',
            'title': 'Solidity Smart Contract Development',
            'slug': 'solidity-smart-contracts',
            'description': 'Ethereum development, smart contracts, and DeFi protocols',
            'duration': 4
        },
        {
            'sector': 'blockchain-web3',
            'title': 'Blockchain Development Internship',
            'slug': 'blockchain-dev',
            'description': 'Bitcoin, Ethereum, consensus mechanisms, and blockchain architecture',
            'duration': 4
        },
        {
            'sector': 'blockchain-web3',
            'title': 'Web3 & DeFi Protocol Development',
            'slug': 'web3-defi-dev',
            'description': 'DeFi, cryptocurrency, tokenomics, and decentralized applications',
            'duration': 4
        },
        
        # GAME DEVELOPMENT
        {
            'sector': 'game-development',
            'title': 'Unity Game Engine Development',
            'slug': 'unity-game-dev',
            'description': 'C# game development, physics, graphics, and game mechanics',
            'duration': 4
        },
        {
            'sector': 'game-development',
            'title': 'Unreal Engine 5 Game Development',
            'slug': 'unreal-game-dev',
            'description': 'C++ Unreal development, advanced graphics, and 3D game creation',
            'duration': 4
        },
        {
            'sector': 'game-development',
            'title': 'Game Design & Graphics Programming',
            'slug': 'game-design-graphics',
            'description': 'Game design, graphics API, shaders, and visual effects',
            'duration': 4
        },
        
        # QA & TESTING
        {
            'sector': 'qa-testing',
            'title': 'Automation Testing with Selenium',
            'slug': 'automation-selenium',
            'description': 'Web automation testing, test frameworks, and CI/CD integration',
            'duration': 4
        },
        {
            'sector': 'qa-testing',
            'title': 'Performance & Load Testing',
            'slug': 'performance-testing',
            'description': 'JMeter, LoadRunner, stress testing, and performance optimization',
            'duration': 4
        },
        {
            'sector': 'qa-testing',
            'title': 'Manual Testing & QA Strategy',
            'slug': 'manual-testing-qa',
            'description': 'Test case design, bug reporting, and QA methodologies',
            'duration': 4
        },
        
        # DESIGN & UX/UI
        {
            'sector': 'design-ux-ui',
            'title': 'UI/UX Design Internship',
            'slug': 'ui-ux-design',
            'description': 'Figma, user research, wireframing, and interaction design',
            'duration': 4
        },
        {
            'sector': 'design-ux-ui',
            'title': 'Graphic Design & Web Design',
            'slug': 'graphic-web-design',
            'description': 'Adobe Creative Suite, visual design, and branding',
            'duration': 4
        },
        
        # BUSINESS & MANAGEMENT
        {
            'sector': 'business-management',
            'title': 'Product Management Internship',
            'slug': 'product-management',
            'description': 'Product strategy, roadmapping, and stakeholder management',
            'duration': 4
        },
        {
            'sector': 'business-management',
            'title': 'Project Management & Agile',
            'slug': 'project-management-agile',
            'description': 'Scrum, Kanban, project planning, and team coordination',
            'duration': 4
        },
        {
            'sector': 'business-management',
            'title': 'Business Analysis Internship',
            'slug': 'business-analysis',
            'description': 'Requirements gathering, process analysis, and business strategy',
            'duration': 4
        },
        
        # MARKETING & DIGITAL
        {
            'sector': 'marketing-digital',
            'title': 'Digital Marketing Internship',
            'slug': 'digital-marketing',
            'description': 'SEO, SEM, content marketing, and digital strategy',
            'duration': 4
        },
        {
            'sector': 'marketing-digital',
            'title': 'Content Marketing & SEO',
            'slug': 'content-marketing-seo',
            'description': 'Blog writing, keyword research, and content optimization',
            'duration': 4
        },
        
        # FINANCE & BANKING
        {
            'sector': 'finance-banking',
            'title': 'Fintech Development Internship',
            'slug': 'fintech-dev',
            'description': 'Payment systems, financial APIs, and fintech platforms',
            'duration': 4
        },
        {
            'sector': 'finance-banking',
            'title': 'Financial Analysis & Trading',
            'slug': 'financial-analysis-trading',
            'description': 'Quantitative analysis, algorithmic trading, and market analysis',
            'duration': 4
        },
    ]
    
    count = 0
    for internship in internships:
        sector_id = sector_map.get(internship['sector'])
        if not sector_id:
            print(f"⚠️  Sector not found: {internship['sector']}")
            continue
        
        existing = query_db(
            "SELECT id FROM internships WHERE slug = ?",
            (internship['slug'],),
            one=True
        )
        
        if not existing:
            internship_id = str(uuid.uuid4())
            execute_db(
                """INSERT INTO internships 
                   (id, sector_id, title, slug, short_description, 
                    full_description, duration_weeks, mode, is_featured)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    internship_id,
                    sector_id,
                    internship['title'],
                    internship['slug'],
                    internship['description'],
                    internship['description'],
                    internship['duration'],
                    'Virtual',
                    False
                )
            )
            count += 1
            print(f"✅ Created internship: {internship['title']}")
        else:
            print(f"⏭️  Internship already exists: {internship['title']}")
    
    print(f"\n📊 Total new internships created: {count}")

def seed_internship_tasks():
    """Create weekly tasks for internships"""
    # Get all internships
    internships = query_db("SELECT id, title FROM internships LIMIT 5")
    
    for internship in internships:
        tasks = [
            {
                'week': 1,
                'title': 'Project Setup & Environment Configuration',
                'objective': 'Set up development environment and project structure',
                'deliverables': 'Configured environment, project documentation',
                'steps': '1. Install dependencies, 2. Configure IDE, 3. Create project structure'
            },
            {
                'week': 2,
                'title': 'Core Feature Implementation',
                'objective': 'Implement main functionality and features',
                'deliverables': 'Working features with unit tests',
                'steps': '1. Design architecture, 2. Implement features, 3. Write tests'
            },
            {
                'week': 3,
                'title': 'Integration & Testing',
                'objective': 'Integrate components and perform comprehensive testing',
                'deliverables': 'Integrated code, test reports',
                'steps': '1. Integrate modules, 2. Run integration tests, 3. Bug fixes'
            },
            {
                'week': 4,
                'title': 'Documentation & Deployment',
                'objective': 'Complete documentation and prepare for deployment',
                'deliverables': 'API documentation, deployment guide, project summary',
                'steps': '1. Write documentation, 2. Deploy project, 3. Create summary'
            }
        ]
        
        for task in tasks:
            existing = query_db(
                "SELECT id FROM internship_tasks WHERE internship_id = ? AND week_number = ?",
                (internship['id'], task['week']),
                one=True
            )
            
            if not existing:
                task_id = str(uuid.uuid4())
                execute_db(
                    """INSERT INTO internship_tasks
                       (id, internship_id, week_number, title, objective, deliverables, key_steps)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        task_id,
                        internship['id'],
                        task['week'],
                        task['title'],
                        task['objective'],
                        task['deliverables'],
                        task['steps']
                    )
                )
                print(f"✅ Created task: Week {task['week']} for {internship['title']}")

def main():
    """Run all seeding functions"""
    print("=" * 80)
    print("🌱 COMPREHENSIVE INTERNSHIP SEEDING SCRIPT")
    print("=" * 80)
    
    print("\n📚 Step 1: Seeding Sectors...")
    print("-" * 80)
    seed_sectors()
    
    print("\n💼 Step 2: Seeding Internships...")
    print("-" * 80)
    seed_internships()
    
    print("\n📋 Step 3: Seeding Internship Tasks...")
    print("-" * 80)
    seed_internship_tasks()
    
    print("\n" + "=" * 80)
    print("✅ SEEDING COMPLETE!")
    print("=" * 80)
    print("\nSummary:")
    print(f"  • Sectors: {query_db('SELECT COUNT(*) as count FROM sectors', one=True)['count']}")
    print(f"  • Internships: {query_db('SELECT COUNT(*) as count FROM internships', one=True)['count']}")
    print(f"  • Tasks: {query_db('SELECT COUNT(*) as count FROM internship_tasks', one=True)['count']}")
    print("\n🚀 Platform is now ready with comprehensive internship data!")

if __name__ == '__main__':
    main()
