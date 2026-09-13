/**
 * Central Client-Side Persistent Storage Manager
 * Uses IndexedDB for account-scoped data persistence
 * 
 * CRITICAL: All data is tied to the current browser/device storage
 * Data will NOT sync across different devices, browsers, or after storage is cleared
 * 
 * Usage:
 *   await Storage.init();
 *   const userId = "user_" + crypto.randomUUID();
 *   await Storage.saveUser({ userId, name: "John", email: "john@example.com" });
 *   const user = await Storage.getUser(userId);
 */

const Storage = {
  DB_NAME: 'InternshipComLocalDB',
  DB_VERSION: 1,
  
  db: null,
  
  /**
   * Initialize IndexedDB database and object stores
   */
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);
      
      request.onerror = () => {
        console.error('[Storage] Init failed:', request.error);
        reject(request.error);
      };
      
      request.onsuccess = () => {
        this.db = request.result;
        console.log('[Storage] Initialized successfully');
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Object store for user accounts
        if (!db.objectStoreNames.contains('users')) {
          const userStore = db.createObjectStore('users', { keyPath: 'userId' });
          userStore.createIndex('email', 'email', { unique: false });
        }
        
        // Object store for user profiles (additional profile data)
        if (!db.objectStoreNames.contains('profiles')) {
          const profileStore = db.createObjectStore('profiles', { keyPath: 'id' });
          profileStore.createIndex('userId', 'userId', { unique: false });
        }
        
        // Object store for internship enrollments
        if (!db.objectStoreNames.contains('enrollments')) {
          const enrollmentStore = db.createObjectStore('enrollments', { keyPath: 'id' });
          enrollmentStore.createIndex('userId', 'userId', { unique: false });
          enrollmentStore.createIndex('userInternship', ['userId', 'internshipId'], { unique: true });
        }
        
        // Object store for internship applications
        if (!db.objectStoreNames.contains('applications')) {
          const appStore = db.createObjectStore('applications', { keyPath: 'id' });
          appStore.createIndex('userId', 'userId', { unique: false });
          appStore.createIndex('internshipId', 'internshipId', { unique: false });
        }
        
        // Object store for offer letters
        if (!db.objectStoreNames.contains('offerLetters')) {
          const offerStore = db.createObjectStore('offerLetters', { keyPath: 'id' });
          offerStore.createIndex('userId', 'userId', { unique: false });
          offerStore.createIndex('enrollmentId', 'enrollmentId', { unique: false });
        }
        
        // Object store for certificates
        if (!db.objectStoreNames.contains('certificates')) {
          const certStore = db.createObjectStore('certificates', { keyPath: 'id' });
          certStore.createIndex('userId', 'userId', { unique: false });
          certStore.createIndex('enrollmentId', 'enrollmentId', { unique: false });
        }
        
        // Object store for activities and submissions
        if (!db.objectStoreNames.contains('activities')) {
          const activityStore = db.createObjectStore('activities', { keyPath: 'id' });
          activityStore.createIndex('userId', 'userId', { unique: false });
          activityStore.createIndex('enrollmentId', 'enrollmentId', { unique: false });
        }
        
        // Object store for progress tracking
        if (!db.objectStoreNames.contains('progress')) {
          const progressStore = db.createObjectStore('progress', { keyPath: 'id' });
          progressStore.createIndex('userId', 'userId', { unique: false });
          progressStore.createIndex('enrollmentId', 'enrollmentId', { unique: false });
        }
        
        // Object store for documents (blobs, PDFs, etc.)
        if (!db.objectStoreNames.contains('documents')) {
          const docStore = db.createObjectStore('documents', { keyPath: 'id' });
          docStore.createIndex('userId', 'userId', { unique: false });
          docStore.createIndex('type', 'type', { unique: false });
        }
        
        // Object store for session/auth metadata (small, non-account-specific data)
        if (!db.objectStoreNames.contains('session')) {
          db.createObjectStore('session', { keyPath: 'key' });
        }
        
        console.log('[Storage] Database schema created/upgraded');
      };
    });
  },
  
  /**
   * Get transaction for read/write operations
   */
  getTransaction(storeName, mode = 'readonly') {
    if (!this.db) throw new Error('Storage not initialized');
    return this.db.transaction(storeName, mode);
  },
  
  /**
   * ==================== USER MANAGEMENT ====================
   */
  
  async saveUser(user) {
    if (!user.userId) throw new Error('userId is required');
    const transaction = this.getTransaction('users', 'readwrite');
    const store = transaction.objectStore('users');
    
    const userData = {
      userId: user.userId,
      name: user.name || '',
      email: user.email || '',
      phone: user.phone || '',
      college: user.college || '',
      department: user.department || '',
      degree: user.degree || '',
      createdAt: user.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...user
    };
    
    return new Promise((resolve, reject) => {
      const request = store.put(userData);
      request.onsuccess = () => resolve(userData);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getUser(userId) {
    const transaction = this.getTransaction('users', 'readonly');
    const store = transaction.objectStore('users');
    
    return new Promise((resolve, reject) => {
      const request = store.get(userId);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getUserByEmail(email) {
    if (!email) return null;
    const transaction = this.getTransaction('users', 'readonly');
    const index = transaction.objectStore('users').index('email');
    
    return new Promise((resolve, reject) => {
      const request = index.get(email.toLowerCase());
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  },
  
  async deleteUser(userId) {
    const transaction = this.getTransaction('users', 'readwrite');
    const store = transaction.objectStore('users');
    
    return new Promise((resolve, reject) => {
      const request = store.delete(userId);
      request.onsuccess = () => resolve(true);
      request.onerror = () => reject(request.error);
    });
  },
  
  /**
   * ==================== ENROLLMENT MANAGEMENT ====================
   */
  
  async saveEnrollment(enrollment) {
    if (!enrollment.userId || !enrollment.internshipId) {
      throw new Error('userId and internshipId are required');
    }
    
    const transaction = this.getTransaction('enrollments', 'readwrite');
    const store = transaction.objectStore('enrollments');
    
    const enrollmentData = {
      id: enrollment.id || `enrollment_${crypto.randomUUID()}`,
      userId: enrollment.userId,
      internshipId: enrollment.internshipId,
      internshipTitle: enrollment.internshipTitle || '',
      companyName: enrollment.companyName || '',
      sectorName: enrollment.sectorName || '',
      emoji: enrollment.emoji || '💼',
      status: enrollment.status || 'enrolled',
      progress: enrollment.progress || 0,
      enrolledAt: enrollment.enrolledAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      durationWeeks: enrollment.durationWeeks || 4,
      completedWeeks: enrollment.completedWeeks || 0,
      startDate: enrollment.startDate || '',
      endDate: enrollment.endDate || '',
      ...enrollment
    };
    
    return new Promise((resolve, reject) => {
      const request = store.put(enrollmentData);
      request.onsuccess = () => resolve(enrollmentData);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getEnrollment(enrollmentId) {
    const transaction = this.getTransaction('enrollments', 'readonly');
    const store = transaction.objectStore('enrollments');
    
    return new Promise((resolve, reject) => {
      const request = store.get(enrollmentId);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getUserEnrollments(userId) {
    const transaction = this.getTransaction('enrollments', 'readonly');
    const index = transaction.objectStore('enrollments').index('userId');
    
    return new Promise((resolve, reject) => {
      const request = index.getAll(userId);
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getEnrollmentByInternship(userId, internshipId) {
    const transaction = this.getTransaction('enrollments', 'readonly');
    const index = transaction.objectStore('enrollments').index('userInternship');
    
    return new Promise((resolve, reject) => {
      const request = index.get([userId, internshipId]);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  },
  
  async deleteEnrollment(enrollmentId) {
    const transaction = this.getTransaction('enrollments', 'readwrite');
    const store = transaction.objectStore('enrollments');
    
    return new Promise((resolve, reject) => {
      const request = store.delete(enrollmentId);
      request.onsuccess = () => resolve(true);
      request.onerror = () => reject(request.error);
    });
  },
  
  /**
   * ==================== APPLICATION MANAGEMENT ====================
   */
  
  async saveApplication(application) {
    if (!application.userId) throw new Error('userId is required');
    
    const transaction = this.getTransaction('applications', 'readwrite');
    const store = transaction.objectStore('applications');
    
    const appData = {
      id: application.id || `application_${crypto.randomUUID()}`,
      userId: application.userId,
      internshipId: application.internshipId || '',
      internshipTitle: application.internshipTitle || '',
      status: application.status || 'active',
      submittedAt: application.submittedAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...application
    };
    
    return new Promise((resolve, reject) => {
      const request = store.put(appData);
      request.onsuccess = () => resolve(appData);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getUserApplications(userId) {
    const transaction = this.getTransaction('applications', 'readonly');
    const index = transaction.objectStore('applications').index('userId');
    
    return new Promise((resolve, reject) => {
      const request = index.getAll(userId);
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  },
  
  /**
   * ==================== OFFER LETTER MANAGEMENT ====================
   */
  
  async saveOfferLetter(offerLetter) {
    if (!offerLetter.userId) throw new Error('userId is required');
    
    const transaction = this.getTransaction('offerLetters', 'readwrite');
    const store = transaction.objectStore('offerLetters');
    
    const offerData = {
      id: offerLetter.id || `offer_${crypto.randomUUID()}`,
      userId: offerLetter.userId,
      enrollmentId: offerLetter.enrollmentId || '',
      internshipId: offerLetter.internshipId || '',
      candidateName: offerLetter.candidateName || '',
      internshipTitle: offerLetter.internshipTitle || '',
      companyName: offerLetter.companyName || '',
      issueDate: offerLetter.issueDate || new Date().toISOString(),
      startDate: offerLetter.startDate || '',
      endDate: offerLetter.endDate || '',
      status: offerLetter.status || 'issued',
      documentNumber: offerLetter.documentNumber || '',
      documentData: offerLetter.documentData || null, // Can store HTML or blob
      createdAt: offerLetter.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...offerLetter
    };
    
    return new Promise((resolve, reject) => {
      const request = store.put(offerData);
      request.onsuccess = () => resolve(offerData);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getOfferLetter(offerId) {
    const transaction = this.getTransaction('offerLetters', 'readonly');
    const store = transaction.objectStore('offerLetters');
    
    return new Promise((resolve, reject) => {
      const request = store.get(offerId);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getUserOfferLetters(userId) {
    const transaction = this.getTransaction('offerLetters', 'readonly');
    const index = transaction.objectStore('offerLetters').index('userId');
    
    return new Promise((resolve, reject) => {
      const request = index.getAll(userId);
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  },
  
  /**
   * ==================== CERTIFICATE MANAGEMENT ====================
   */
  
  async saveCertificate(certificate) {
    if (!certificate.userId) throw new Error('userId is required');
    
    const transaction = this.getTransaction('certificates', 'readwrite');
    const store = transaction.objectStore('certificates');
    
    const certData = {
      id: certificate.id || `cert_${crypto.randomUUID()}`,
      userId: certificate.userId,
      enrollmentId: certificate.enrollmentId || '',
      internshipId: certificate.internshipId || '',
      certificateNumber: certificate.certificateNumber || '',
      candidateName: certificate.candidateName || '',
      internshipTitle: certificate.internshipTitle || '',
      issueDate: certificate.issueDate || new Date().toISOString(),
      status: certificate.status || 'issued',
      documentData: certificate.documentData || null, // Can store HTML or blob
      isPaid: certificate.isPaid || false,
      createdAt: certificate.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...certificate
    };
    
    return new Promise((resolve, reject) => {
      const request = store.put(certData);
      request.onsuccess = () => resolve(certData);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getCertificate(certId) {
    const transaction = this.getTransaction('certificates', 'readonly');
    const store = transaction.objectStore('certificates');
    
    return new Promise((resolve, reject) => {
      const request = store.get(certId);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getUserCertificates(userId) {
    const transaction = this.getTransaction('certificates', 'readonly');
    const index = transaction.objectStore('certificates').index('userId');
    
    return new Promise((resolve, reject) => {
      const request = index.getAll(userId);
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  },
  
  /**
   * ==================== ACTIVITY & PROGRESS MANAGEMENT ====================
   */
  
  async saveActivity(activity) {
    if (!activity.userId) throw new Error('userId is required');
    
    const transaction = this.getTransaction('activities', 'readwrite');
    const store = transaction.objectStore('activities');
    
    const actData = {
      id: activity.id || `activity_${crypto.randomUUID()}`,
      userId: activity.userId,
      enrollmentId: activity.enrollmentId || '',
      activityType: activity.activityType || '', // e.g., 'submission', 'task_completion'
      description: activity.description || '',
      status: activity.status || 'pending',
      createdAt: activity.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...activity
    };
    
    return new Promise((resolve, reject) => {
      const request = store.put(actData);
      request.onsuccess = () => resolve(actData);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getActivities(userId, enrollmentId = null) {
    const transaction = this.getTransaction('activities', 'readonly');
    const index = transaction.objectStore('activities').index('userId');
    
    return new Promise((resolve, reject) => {
      const request = index.getAll(userId);
      request.onsuccess = () => {
        let activities = request.result || [];
        if (enrollmentId) {
          activities = activities.filter(a => a.enrollmentId === enrollmentId);
        }
        resolve(activities);
      };
      request.onerror = () => reject(request.error);
    });
  },
  
  async saveProgress(progress) {
    if (!progress.userId) throw new Error('userId is required');
    
    const transaction = this.getTransaction('progress', 'readwrite');
    const store = transaction.objectStore('progress');
    
    const progData = {
      id: progress.id || `progress_${crypto.randomUUID()}`,
      userId: progress.userId,
      enrollmentId: progress.enrollmentId || '',
      percentComplete: progress.percentComplete || 0,
      completedTasks: progress.completedTasks || 0,
      totalTasks: progress.totalTasks || 0,
      updatedAt: new Date().toISOString(),
      ...progress
    };
    
    return new Promise((resolve, reject) => {
      const request = store.put(progData);
      request.onsuccess = () => resolve(progData);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getProgress(progressId) {
    const transaction = this.getTransaction('progress', 'readonly');
    const store = transaction.objectStore('progress');
    
    return new Promise((resolve, reject) => {
      const request = store.get(progressId);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  },
  
  /**
   * ==================== DOCUMENT MANAGEMENT ====================
   */
  
  async saveDocument(document) {
    if (!document.userId) throw new Error('userId is required');
    
    const transaction = this.getTransaction('documents', 'readwrite');
    const store = transaction.objectStore('documents');
    
    const docData = {
      id: document.id || `doc_${crypto.randomUUID()}`,
      userId: document.userId,
      type: document.type || '', // e.g., 'offer_letter', 'certificate', 'resume'
      name: document.name || '',
      content: document.content || null, // Blob or data URL
      createdAt: document.createdAt || new Date().toISOString(),
      ...document
    };
    
    return new Promise((resolve, reject) => {
      const request = store.put(docData);
      request.onsuccess = () => resolve(docData);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getDocument(docId) {
    const transaction = this.getTransaction('documents', 'readonly');
    const store = transaction.objectStore('documents');
    
    return new Promise((resolve, reject) => {
      const request = store.get(docId);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  },
  
  /**
   * ==================== SESSION MANAGEMENT ====================
   */
  
  async setSessionValue(key, value) {
    const transaction = this.getTransaction('session', 'readwrite');
    const store = transaction.objectStore('session');
    
    return new Promise((resolve, reject) => {
      const request = store.put({ key, value });
      request.onsuccess = () => resolve(value);
      request.onerror = () => reject(request.error);
    });
  },
  
  async getSessionValue(key) {
    const transaction = this.getTransaction('session', 'readonly');
    const store = transaction.objectStore('session');
    
    return new Promise((resolve, reject) => {
      const request = store.get(key);
      request.onsuccess = () => resolve(request.result?.value || null);
      request.onerror = () => reject(request.error);
    });
  },
  
  async clearSession() {
    const transaction = this.getTransaction('session', 'readwrite');
    const store = transaction.objectStore('session');
    
    return new Promise((resolve, reject) => {
      const request = store.clear();
      request.onsuccess = () => resolve(true);
      request.onerror = () => reject(request.error);
    });
  },
  
  /**
   * ==================== ACCOUNT RESTORATION ====================
   */
  
  async restoreUserAccount(userId) {
    try {
      const profile = await this.getUser(userId);
      const enrollments = await this.getUserEnrollments(userId);
      const applications = await this.getUserApplications(userId);
      const offerLetters = await this.getUserOfferLetters(userId);
      const certificates = await this.getUserCertificates(userId);
      const activities = await this.getActivities(userId);
      
      return {
        profile,
        enrollments,
        applications,
        offerLetters,
        certificates,
        activities,
        restoredAt: new Date().toISOString()
      };
    } catch (error) {
      console.error('[Storage] Account restoration failed:', error);
      throw error;
    }
  },
  
  /**
   * ==================== MIGRATION & CLEANUP ====================
   */
  
  async clearAllUserData(userId) {
    // This should NEVER be called on logout
    // Only for explicit user-initiated account deletion
    try {
      const stores = [
        'enrollments',
        'applications',
        'offerLetters',
        'certificates',
        'activities',
        'progress',
        'documents'
      ];
      
      for (const storeName of stores) {
        const transaction = this.getTransaction(storeName, 'readwrite');
        const index = transaction.objectStore(storeName).index('userId');
        
        await new Promise((resolve, reject) => {
          const request = index.getAll(userId);
          request.onsuccess = () => {
            const records = request.result || [];
            records.forEach(record => {
              transaction.objectStore(storeName).delete(record.id);
            });
            resolve();
          };
          request.onerror = () => reject(request.error);
        });
      }
      
      // Remove user record itself
      await this.deleteUser(userId);
      
      console.log('[Storage] All data cleared for user:', userId);
      return true;
    } catch (error) {
      console.error('[Storage] Clear all data failed:', error);
      throw error;
    }
  },
  
  /**
   * Check if IndexedDB is available
   */
  isAvailable() {
    try {
      return !!window.indexedDB;
    } catch (e) {
      return false;
    }
  }
};

// Auto-initialize storage when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  try {
    if (Storage.isAvailable()) {
      await Storage.init();
      console.log('[Storage] Ready for use');
    } else {
      console.warn('[Storage] IndexedDB not available');
    }
  } catch (error) {
    console.error('[Storage] Initialization error:', error);
  }
});
