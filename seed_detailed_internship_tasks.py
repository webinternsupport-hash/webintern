"""
Comprehensive Internship Tasks Seeding Script
Creates detailed, internship-specific tasks with 10+ line descriptions
"""

import uuid
from database import execute_db, query_db

def seed_internship_tasks_detailed():
    """Create comprehensive, detailed tasks for all internships"""
    
    # Get all internships
    internships = query_db("SELECT id, title, slug FROM internships")
    
    task_templates = {
        'python-backend-dev': [
            {
                'week': 1,
                'title': 'Python Environment Setup & Django Basics',
                'objective': 'Set up Python development environment with Django framework and understand MVC architecture',
                'deliverables': 'Working Django project with models, views, and URL routing configured',
                'key_steps': '''
1. Install Python 3.9+ and create virtual environment
2. Install Django using pip (latest version)
3. Create new Django project structure with proper organization
4. Configure database settings (SQLite for development)
5. Create Django app for user management
6. Define models for User, Profile, and Preferences
7. Create basic views for user listing and detail pages
8. Set up URL routing for all created views
9. Test database migrations and ORM functionality
10. Create basic templates with Django template language
11. Implement static files handling for CSS and JavaScript
12. Set up Django admin interface for model management
13. Create simple forms for user input
14. Test all functionality locally
15. Document setup process and configurations
                '''
            },
            {
                'week': 2,
                'title': 'Build RESTful API with Django REST Framework',
                'objective': 'Create production-ready REST APIs with proper authentication and permissions',
                'deliverables': 'Fully functional REST API with CRUD operations, authentication, and pagination',
                'key_steps': '''
1. Install and configure Django REST Framework
2. Create serializers for all database models
3. Implement ViewSets for comprehensive CRUD operations
4. Configure URL routing for all API endpoints
5. Implement JWT token-based authentication
6. Add permission classes for authorization
7. Create custom permission classes for business logic
8. Implement pagination for large datasets
9. Add filtering and search capabilities
10. Implement API versioning strategy
11. Add comprehensive error handling and validation
12. Create API documentation using DRF's browsable API
13. Implement rate limiting for API protection
14. Add CORS headers for cross-origin requests
15. Test all API endpoints with Postman or similar tool
16. Document all API endpoints with examples
17. Create unit tests for API functionality
                '''
            },
            {
                'week': 3,
                'title': 'Database Optimization & Query Performance',
                'objective': 'Optimize database queries and implement caching strategies',
                'deliverables': 'Optimized database with proper indexing, query caching, and performance tests',
                'key_steps': '''
1. Analyze current database queries using Django debug toolbar
2. Identify N+1 query problems in API endpoints
3. Implement select_related() for foreign key optimization
4. Implement prefetch_related() for many-to-many relationships
5. Add database indexes to frequently queried fields
6. Create composite indexes for complex queries
7. Implement Redis caching for frequently accessed data
8. Set up cache invalidation strategies
9. Configure Celery for asynchronous task processing
10. Implement pagination to reduce query results
11. Use database connection pooling
12. Create raw SQL queries where needed for complex operations
13. Profile database performance with query execution plans
14. Document all optimization decisions and rationale
15. Write performance tests with benchmark data
16. Monitor query performance in production
                '''
            },
            {
                'week': 4,
                'title': 'Testing, Documentation & Deployment',
                'objective': 'Write comprehensive tests, documentation, and deploy application',
                'deliverables': 'Production-ready application with 80%+ test coverage, complete documentation, and deployment guide',
                'key_steps': '''
1. Write unit tests for all business logic
2. Create integration tests for API endpoints
3. Implement test fixtures and factories
4. Set up continuous integration with GitHub Actions
5. Configure code coverage reporting
6. Write API documentation with examples
7. Create deployment documentation
8. Set up environment variables for different environments
9. Configure logging and monitoring
10. Create Docker configuration for containerization
11. Set up database migration scripts
12. Implement health check endpoints
13. Configure error tracking with Sentry
14. Set up application performance monitoring
15. Create troubleshooting guide
16. Write deployment checklist
17. Conduct security audit and fix vulnerabilities
18. Document all dependencies and versions
19. Create backup and recovery procedures
20. Test deployment process in staging environment
                '''
            }
        ],
        'c-programming-fundamentals': [
            {
                'week': 1,
                'title': 'C Basics: Variables, Data Types, and Control Flow',
                'objective': 'Master C syntax, variable declarations, data types, and conditional statements',
                'deliverables': 'Five C programs demonstrating variables, loops, conditionals, and basic I/O',
                'key_steps': '''
1. Set up C development environment (GCC compiler, VS Code or IDE)
2. Write program to declare various data types (int, float, char, double)
3. Understand and demonstrate variable scope (local vs global)
4. Create program with if-else statements for conditional logic
5. Write switch-case program for multi-way branching
6. Implement while loop for iteration
7. Create for loop program with nested loops
8. Write do-while loop example
9. Implement break and continue statements
10. Create program using ternary operator
11. Demonstrate operator precedence
12. Write program combining multiple control structures
13. Create menu-driven program with user input
14. Implement input validation
15. Debug programs using print statements
16. Understand and handle compilation errors
17. Test programs with various input values
                '''
            },
            {
                'week': 2,
                'title': 'Arrays, Strings, and Functions in C',
                'objective': 'Work with arrays, strings, and modular programming using functions',
                'deliverables': 'Programs demonstrating arrays, string manipulation, function definitions, and parameter passing',
                'key_steps': '''
1. Create one-dimensional array programs (declaration, initialization)
2. Implement array operations (searching, sorting, filtering)
3. Create two-dimensional array programs (matrices)
4. Write program for 3D array operations
5. Demonstrate array passing to functions
6. Implement string basics (character arrays)
7. Use string library functions (strlen, strcpy, strcat, strcmp)
8. Create custom string manipulation functions
9. Write program for string parsing
10. Implement pattern matching in strings
11. Create function with no parameters and no return
12. Write function with parameters and return values
13. Implement recursive functions (factorial, fibonacci)
14. Create function for sorting arrays
15. Implement function for searching in arrays
16. Write program using local and global variables
17. Create static variables demonstration
18. Implement pass-by-value and pass-by-reference
19. Write function documentation
20. Test functions with multiple test cases
                '''
            },
            {
                'week': 3,
                'title': 'Pointers and Dynamic Memory Management',
                'objective': 'Master pointer concepts and dynamic memory allocation',
                'deliverables': 'Programs demonstrating pointers, memory allocation, and dynamic data structures',
                'key_steps': '''
1. Understand and declare pointer variables
2. Use address-of (&) and dereference (*) operators
3. Create array of pointers
4. Implement pointer to pointer (double pointer)
5. Write program for dynamic memory allocation (malloc)
6. Implement dynamic array creation
7. Use calloc for memory allocation with initialization
8. Implement realloc for memory resizing
9. Write program demonstrating memory leaks
10. Create function to free dynamically allocated memory
11. Build linked list with pointers
12. Implement pointer arithmetic for array traversal
13. Create function pointers for callbacks
14. Write program using void pointers
15. Implement function returning pointer
16. Create dynamic 2D array
17. Implement pointer to function array
18. Write program for parameter passing via pointers
19. Debug memory issues using valgrind
20. Test memory allocation and deallocation
                '''
            },
            {
                'week': 4,
                'title': 'Data Structures: Linked Lists and Introduction to Algorithms',
                'objective': 'Implement basic data structures and fundamental algorithms',
                'deliverables': 'Complete linked list implementation with insert, delete, search, and sorting algorithms',
                'key_steps': '''
1. Design node structure for linked list
2. Implement linked list creation and traversal
3. Create insert function (at beginning, end, middle)
4. Implement delete function (first, last, at position)
5. Write search function for linked list
6. Implement display/print function
7. Create reverse linked list function
8. Write function to find middle element
9. Implement detect cycle in linked list
10. Create merge sorted linked lists
11. Implement bubble sort algorithm
12. Write selection sort program
13. Create insertion sort implementation
14. Implement linear search
15. Write binary search with sorted array
16. Create program to find maximum element
17. Implement reverse array algorithm
18. Write program for array rotation
19. Create palindrome checking function
20. Test all implementations with various inputs and edge cases
                '''
            }
        ],
        'react-frontend-dev': [
            {
                'week': 1,
                'title': 'React Setup and Component Fundamentals',
                'objective': 'Set up React development environment and create functional components',
                'deliverables': 'React app with multiple functional components, JSX rendering, and component composition',
                'key_steps': '''
1. Install Node.js and npm package manager
2. Create React app using Create React App or Vite
3. Understand project structure and dependencies
4. Create first functional component
5. Learn JSX syntax and rules
6. Implement component props and prop passing
7. Create components that accept and use props
8. Build component hierarchy
9. Create reusable UI components
10. Implement conditional rendering
11. Create list rendering with map()
12. Implement key prop for list items
13. Create components with default props
14. Implement prop types validation
15. Build component composition examples
16. Create components folder structure
17. Export and import components correctly
18. Test components with different props
19. Understand virtual DOM concept
20. Learn component lifecycle basics
                '''
            },
            {
                'week': 2,
                'title': 'State Management and Event Handling',
                'objective': 'Master React state, hooks, and event handling',
                'deliverables': 'Interactive React components with state management, event handlers, and form handling',
                'key_steps': '''
1. Understand useState hook
2. Create stateful functional components
3. Update state with setState
4. Implement multiple state variables
5. Create event handlers (click, change, submit)
6. Build form with controlled inputs
7. Implement form validation
8. Create todo list with add/delete functionality
9. Implement counter with increment/decrement
10. Create form with multiple input fields
11. Build checkbox and radio button handlers
12. Implement select dropdown handling
13. Create text input with character limit
14. Build form submission handler
15. Implement error message display
16. Create conditional rendering based on state
17. Build component with toggle functionality
18. Implement state lifting to parent component
19. Create child-to-parent communication
20. Test all state management scenarios
                '''
            },
            {
                'week': 3,
                'title': 'Hooks, Effects, and Advanced State Management',
                'objective': 'Master React hooks and side effects handling',
                'deliverables': 'Applications using useEffect, useContext, custom hooks, and advanced state patterns',
                'key_steps': '''
1. Understand useEffect hook
2. Implement side effects (API calls, timers)
3. Create cleanup functions in useEffect
4. Use dependency arrays correctly
5. Create custom hooks for reusable logic
6. Implement data fetching in useEffect
7. Build API integration component
8. Create loading and error states
9. Implement useContext for global state
10. Create context providers and consumers
11. Build theme switcher using context
12. Implement useReducer for complex state
13. Create reducer functions
14. Combine useReducer with useContext
15. Build shopping cart with useReducer
16. Implement useCallback for optimization
17. Use useMemo for performance
18. Create useRef for DOM access
19. Build controlled/uncontrolled component examples
20. Implement error boundary patterns
                '''
            },
            {
                'week': 4,
                'title': 'Routing, Styling, and Project Deployment',
                'objective': 'Build multi-page applications with routing and styling',
                'deliverables': 'Complete React application with routing, styling, and deployed to production',
                'key_steps': '''
1. Install and configure React Router
2. Create route definitions
3. Implement page components
4. Create navigation links and navigation bar
5. Implement dynamic routing with parameters
6. Build nested routes
7. Create redirects and not found pages
8. Implement programmatic navigation
9. Build query parameters handling
10. Create CSS modules for component styling
11. Implement CSS-in-JS with styled-components
12. Create responsive design with flexbox/grid
13. Build mobile-first design
14. Implement media queries
15. Create reusable CSS utilities
16. Build component library with storybook
17. Optimize performance with code splitting
18. Implement lazy loading with React.lazy
19. Create production build
20. Deploy to Netlify/Vercel with continuous deployment
                '''
            }
        ]
    }
    
    # If no specific template, use default
    default_template = [
        {
            'week': 1,
            'title': 'Foundation & Environment Setup',
            'objective': 'Set up development environment and understand fundamentals',
            'deliverables': 'Working setup with documentation and basic examples',
            'key_steps': '''
1. Install required software and tools
2. Set up development environment
3. Configure IDE or code editor
4. Understand project structure and organization
5. Create starter project or application
6. Review and understand key concepts
7. Complete basic tutorials
8. Create documentation of setup process
9. Test all tools are working correctly
10. Create checklist of dependencies
11. Understand version control basics
12. Create GitHub/Git repository
13. Learn basic Git commands
14. Understand project architecture
15. Review best practices for the technology
16. Set up development folder structure
17. Create README with setup instructions
18. Test development environment
19. Document all configurations
20. Prepare for next week\'s development
            '''
        },
        {
            'week': 2,
            'title': 'Core Feature Implementation',
            'objective': 'Build main features and core functionality',
            'deliverables': 'Working features with documentation and test coverage',
            'key_steps': '''
1. Design application architecture
2. Identify and list all features needed
3. Break features into smaller tasks
4. Implement first core feature
5. Write unit tests for features
6. Create feature documentation
7. Implement error handling
8. Add logging and debugging
9. Create sample data for testing
10. Test features thoroughly
11. Get code review from mentor
12. Fix any identified issues
13. Implement second core feature
14. Test feature integration
15. Document API or interface
16. Create user documentation
17. Implement edge case handling
18. Performance testing
19. Security review
20. Prepare for integration testing
            '''
        },
        {
            'week': 3,
            'title': 'Integration & Testing',
            'objective': 'Integrate components and perform comprehensive testing',
            'deliverables': 'Fully integrated system with test report and documentation',
            'key_steps': '''
1. Create test plan
2. Write integration tests
3. Test feature interactions
4. Implement end-to-end testing
5. Test data flow between components
6. Create test scenarios
7. Test error scenarios
8. Performance optimization
9. Load testing
10. Security testing
11. User acceptance testing
12. Fix bugs found during testing
13. Document test results
14. Create troubleshooting guide
15. Implement monitoring
16. Test with real data
17. Test edge cases
18. Performance profiling
19. Optimization implementation
20. Final quality check
            '''
        },
        {
            'week': 4,
            'title': 'Documentation & Deployment',
            'objective': 'Complete documentation and deploy to production',
            'deliverables': 'Production-ready application with complete documentation',
            'key_steps': '''
1. Write comprehensive documentation
2. Create API documentation
3. Create user guide
4. Create installation guide
5. Create configuration guide
6. Write troubleshooting guide
7. Document all dependencies
8. Create deployment checklist
9. Prepare deployment guide
10. Set up production environment
11. Configure logging in production
12. Set up monitoring and alerts
13. Create backup procedures
14. Create rollback procedures
15. Document server configuration
16. Create disaster recovery plan
17. Perform final testing
18. Get approval for deployment
19. Deploy to production
20. Monitor deployed application
            '''
        }
    ]
    
    count = 0
    for internship in internships:
        internship_slug = internship['slug']
        
        # Use specific template if available, otherwise use default
        tasks = task_templates.get(internship_slug, default_template)
        
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
                       (id, internship_id, week_number, title, objective, deliverables, key_steps, evaluation_criteria)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        task_id,
                        internship['id'],
                        task['week'],
                        task['title'],
                        task['objective'],
                        task['deliverables'],
                        task['key_steps'],
                        'Completion of deliverables, code quality, documentation, testing'
                    )
                )
                count += 1
                print(f"✅ Created detailed task: Week {task['week']} for {internship['title']}")
    
    print(f"\n📊 Total detailed tasks created: {count}")

if __name__ == '__main__':
    print("=" * 80)
    print("🌱 DETAILED INTERNSHIP TASKS SEEDING")
    print("=" * 80)
    seed_internship_tasks_detailed()
    print("\n✅ DETAILED TASKS SEEDING COMPLETE!")
