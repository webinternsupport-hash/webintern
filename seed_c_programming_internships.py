"""
C Programming Internship Seeding Script
Adds comprehensive C programming tracks to the platform
"""

import uuid
from database import execute_db, query_db

def seed_c_programming_internships():
    """Create comprehensive C programming internships"""
    
    # Get backend development sector
    backend_sector = query_db(
        "SELECT id FROM sectors WHERE slug = ?",
        ('backend-development',),
        one=True
    )
    
    if not backend_sector:
        print("⚠️  Backend Development sector not found!")
        return
    
    sector_id = backend_sector['id']
    
    c_internships = [
        {
            'title': 'C Programming Fundamentals Internship',
            'slug': 'c-programming-fundamentals',
            'description': 'Master C programming basics: variables, loops, functions, arrays, pointers, and memory management. Perfect for beginners.',
            'duration': 4
        },
        {
            'title': 'C Pointers & Memory Management',
            'slug': 'c-pointers-memory',
            'description': 'Deep dive into C pointers, dynamic memory allocation, and advanced memory management techniques.',
            'duration': 4
        },
        {
            'title': 'C Data Structures Internship',
            'slug': 'c-data-structures',
            'description': 'Learn and implement fundamental data structures: linked lists, stacks, queues, trees, graphs, and hash tables in C.',
            'duration': 4
        },
        {
            'title': 'C Algorithms & Problem Solving',
            'slug': 'c-algorithms-problem-solving',
            'description': 'Master algorithms: sorting, searching, dynamic programming, graph algorithms, and competitive programming with C.',
            'duration': 4
        },
        {
            'title': 'Systems Programming with C',
            'slug': 'c-systems-programming',
            'description': 'Low-level systems programming: file I/O, process management, signals, sockets, and system calls in C.',
            'duration': 4
        },
        {
            'title': 'C Operating Systems Development',
            'slug': 'c-os-development',
            'description': 'Develop operating system concepts: kernels, process scheduling, memory management, and multi-threading in C.',
            'duration': 4
        },
        {
            'title': 'C Embedded Systems Programming',
            'slug': 'c-embedded-systems',
            'description': 'Embedded systems development: microcontroller programming, hardware interaction, real-time systems with C.',
            'duration': 4
        },
        {
            'title': 'C Game Engine Development',
            'slug': 'c-game-engine',
            'description': 'Create game engines and graphics programming with C: SDL, OpenGL, 2D/3D rendering, game physics.',
            'duration': 4
        },
        {
            'title': 'C Database Engine Development',
            'slug': 'c-database-engine',
            'description': 'Build database systems from scratch: data storage, indexing, query processing, and transaction management in C.',
            'duration': 4
        },
        {
            'title': 'C Network Programming Internship',
            'slug': 'c-network-programming',
            'description': 'Network programming with C: TCP/IP, sockets, client-server applications, and protocol implementation.',
            'duration': 4
        },
        {
            'title': 'C Web Server Development',
            'slug': 'c-web-server-dev',
            'description': 'Build lightweight web servers in C: HTTP protocol, request handling, multi-threading, and performance optimization.',
            'duration': 4
        },
        {
            'title': 'C Compiler Development Internship',
            'slug': 'c-compiler-dev',
            'description': 'Learn compiler design: lexical analysis, parsing, code generation, and building a mini C compiler.',
            'duration': 4
        },
        {
            'title': 'C Performance Optimization',
            'slug': 'c-performance-optimization',
            'description': 'Advanced optimization techniques: profiling, algorithmic optimization, memory optimization, and concurrent programming.',
            'duration': 4
        },
        {
            'title': 'C Cryptography & Security',
            'slug': 'c-cryptography-security',
            'description': 'Cryptographic algorithms, secure coding practices, and security libraries implementation in C.',
            'duration': 4
        },
        {
            'title': 'C IoT & Hardware Programming',
            'slug': 'c-iot-hardware',
            'description': 'IoT development with C: Arduino, Raspberry Pi, sensor integration, and firmware development.',
            'duration': 4
        }
    ]
    
    count = 0
    for internship in c_internships:
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
            print(f"✅ Created C internship: {internship['title']}")
        else:
            print(f"⏭️  C internship already exists: {internship['title']}")
    
    return count

def seed_c_advanced_topics():
    """Create advanced C programming specializations"""
    
    backend_sector = query_db(
        "SELECT id FROM sectors WHERE slug = ?",
        ('backend-development',),
        one=True
    )
    
    if not backend_sector:
        return 0
    
    sector_id = backend_sector['id']
    
    advanced_internships = [
        {
            'title': 'C Advanced Concurrency Internship',
            'slug': 'c-advanced-concurrency',
            'description': 'Concurrent programming in C: threads, mutexes, semaphores, condition variables, and synchronization.',
            'duration': 4
        },
        {
            'title': 'C Socket Programming & Networking',
            'slug': 'c-socket-programming',
            'description': 'Advanced socket programming: UDP, TCP, IP multicast, and real-time network applications.',
            'duration': 4
        },
        {
            'title': 'C Graphics & Animation',
            'slug': 'c-graphics-animation',
            'description': 'Graphics programming with C: pixel manipulation, drawing algorithms, animations, and visual effects.',
            'duration': 4
        },
        {
            'title': 'C Linux Kernel Development',
            'slug': 'c-linux-kernel',
            'description': 'Linux kernel development: kernel modules, device drivers, system calls, and kernel internals.',
            'duration': 4
        },
        {
            'title': 'C RTOS Development Internship',
            'slug': 'c-rtos-development',
            'description': 'Real-time operating systems: FreeRTOS, task scheduling, interrupts, and real-time constraints.',
            'duration': 4
        }
    ]
    
    count = 0
    for internship in advanced_internships:
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
            print(f"✅ Created advanced C internship: {internship['title']}")
        else:
            print(f"⏭️  Advanced C internship already exists: {internship['title']}")
    
    return count

def main():
    """Run all C programming seeding functions"""
    print("=" * 80)
    print("🌱 C PROGRAMMING INTERNSHIP SEEDING SCRIPT")
    print("=" * 80)
    
    print("\n📚 Adding Core C Programming Internships...")
    print("-" * 80)
    core_count = seed_c_programming_internships()
    
    print("\n🚀 Adding Advanced C Programming Internships...")
    print("-" * 80)
    advanced_count = seed_c_advanced_topics()
    
    total_added = core_count + advanced_count
    
    print("\n" + "=" * 80)
    print("✅ C PROGRAMMING SEEDING COMPLETE!")
    print("=" * 80)
    print(f"\nC Internships Added:")
    print(f"  • Core C Programming: {core_count} internships")
    print(f"  • Advanced C Topics: {advanced_count} internships")
    print(f"  • Total C Internships: {total_added}")
    
    total_internships = query_db('SELECT COUNT(*) as count FROM internships', one=True)['count']
    print(f"\nTotal Platform Internships: {total_internships}")
    print("\n🎉 C programming tracks are now available on the platform!")
    print("   Students can now search for 'C programming' and find all options.")

if __name__ == '__main__':
    main()
