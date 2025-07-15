// QuantumMeta License Server API Simulation
// This provides client-side API simulation for GitHub Pages deployment

class LicenseAPI {
    constructor() {
        this.baseUrl = window.location.origin;
        this.licenses = this.loadLicenses();
        this.analytics = this.loadAnalytics();
        this.setupRateLimit();
    }

    // Load data from localStorage (simulating a database)
    loadLicenses() {
        const stored = localStorage.getItem('quantummeta_licenses');
        if (stored) {
            return JSON.parse(stored);
        }
        
        // Demo data
        return [
            {
                id: "lic_2025_001",
                user_email: "demo@quantummeta.com",
                user_name: "Demo User",
                packages: ["quantum-metalearn"],
                features: ["core", "pro"],
                machine_id: "5db29cf8e3e8d3f6d1bdffc39e9920d4",
                issued_date: "2025-01-15",
                expires_date: "2026-01-15",
                status: "active",
                license_type: "standard",
                organization: "QuantumMeta Research",
                intended_use: "Research and development",
                created_at: new Date().toISOString()
            },
            {
                id: "lic_2025_002",
                user_email: "researcher@university.edu",
                user_name: "Dr. Jane Smith",
                packages: ["neural-quantum", "kyber-pqc"],
                features: ["core", "research"],
                machine_id: null,
                issued_date: "2025-01-10",
                expires_date: "2025-12-31",
                status: "active",
                license_type: "research",
                organization: "University Research Lab",
                intended_use: "Academic research in quantum computing",
                created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
            }
        ];
    }

    // Load analytics data
    loadAnalytics() {
        const stored = localStorage.getItem('quantummeta_analytics');
        if (stored) {
            return JSON.parse(stored);
        }
        
        return {
            total_licenses: 2847,
            active_users: 1923,
            packages_served: 12,
            uptime: 99.9,
            requests_today: 156,
            licenses_today: 23
        };
    }

    // Save data to localStorage
    saveLicenses() {
        localStorage.setItem('quantummeta_licenses', JSON.stringify(this.licenses));
    }

    saveAnalytics() {
        localStorage.setItem('quantummeta_analytics', JSON.stringify(this.analytics));
    }

    // Rate limiting simulation
    setupRateLimit() {
        this.requestCounts = new Map();
        this.rateLimitWindow = 60000; // 1 minute
        this.maxRequests = 10;
    }

    checkRateLimit(ip = 'demo-ip') {
        const now = Date.now();
        const requests = this.requestCounts.get(ip) || [];
        
        // Remove old requests outside the window
        const validRequests = requests.filter(time => now - time < this.rateLimitWindow);
        
        if (validRequests.length >= this.maxRequests) {
            return false;
        }
        
        validRequests.push(now);
        this.requestCounts.set(ip, validRequests);
        return true;
    }

    // Simulate network delay
    async simulateNetworkDelay(min = 500, max = 2000) {
        const delay = Math.random() * (max - min) + min;
        await new Promise(resolve => setTimeout(resolve, delay));
    }

    // Generate license ID
    generateLicenseId() {
        const year = new Date().getFullYear();
        const sequence = String(this.licenses.length + 1).padStart(3, '0');
        return `lic_${year}_${sequence}`;
    }

    // Generate machine ID
    generateMachineId() {
        const chars = 'abcdef0123456789';
        let result = '';
        for (let i = 0; i < 32; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    }

    // Validate email format
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // API Endpoints

    // POST /api/request-license
    async requestLicense(requestData) {
        await this.simulateNetworkDelay();
        
        if (!this.checkRateLimit()) {
            throw new Error('Rate limit exceeded. Please try again later.');
        }

        // Validate required fields
        if (!requestData.email || !requestData.name || !requestData.packages || requestData.packages.length === 0) {
            throw new Error('Missing required fields: email, name, and packages');
        }

        if (!this.validateEmail(requestData.email)) {
            throw new Error('Invalid email format');
        }

        // Create new license
        const licenseData = {
            id: this.generateLicenseId(),
            user_email: requestData.email,
            user_name: requestData.name,
            packages: requestData.packages,
            features: requestData.features || ['core'],
            machine_id: requestData.machineId || null,
            issued_date: new Date().toISOString().split('T')[0],
            expires_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            status: 'active',
            license_type: requestData.licenseType || 'standard',
            organization: requestData.organization || '',
            intended_use: requestData.intendedUse || '',
            created_at: new Date().toISOString()
        };

        this.licenses.push(licenseData);
        this.saveLicenses();

        // Update analytics
        this.analytics.total_licenses++;
        this.analytics.licenses_today++;
        this.saveAnalytics();

        // Simulate email sending
        await this.sendLicenseEmail(licenseData);

        return {
            success: true,
            license_id: licenseData.id,
            message: 'License generated successfully. Check your email for the .qkey file.',
            email_sent: true,
            download_url: `/api/download/${licenseData.id}`
        };
    }

    // POST /api/validate-license
    async validateLicense(validationData) {
        await this.simulateNetworkDelay(200, 800);
        
        if (!this.checkRateLimit()) {
            throw new Error('Rate limit exceeded. Please try again later.');
        }

        const { licenseId, machineId, packageName } = validationData;
        
        if (!licenseId) {
            throw new Error('License ID is required');
        }

        const license = this.licenses.find(l => l.id === licenseId);
        
        if (!license) {
            return {
                valid: false,
                error: 'License not found',
                code: 'LICENSE_NOT_FOUND'
            };
        }

        // Check expiry
        const now = new Date();
        const expiry = new Date(license.expires_date);
        
        if (now > expiry) {
            return {
                valid: false,
                error: 'License has expired',
                code: 'LICENSE_EXPIRED',
                expires_date: license.expires_date
            };
        }

        // Check status
        if (license.status !== 'active') {
            return {
                valid: false,
                error: `License is ${license.status}`,
                code: 'LICENSE_INACTIVE'
            };
        }

        // Check machine ID if specified
        if (license.machine_id && machineId && license.machine_id !== machineId) {
            return {
                valid: false,
                error: 'Machine ID mismatch',
                code: 'MACHINE_MISMATCH'
            };
        }

        // Check package access
        if (packageName && !license.packages.includes(packageName)) {
            return {
                valid: false,
                error: 'Package not included in license',
                code: 'PACKAGE_NOT_LICENSED'
            };
        }

        return {
            valid: true,
            license_id: license.id,
            packages: license.packages,
            features: license.features,
            expires_date: license.expires_date,
            user_email: license.user_email
        };
    }

    // GET /api/status/{email}
    async getLicenseStatus(email) {
        await this.simulateNetworkDelay(300, 1000);
        
        if (!this.checkRateLimit()) {
            throw new Error('Rate limit exceeded. Please try again later.');
        }

        if (!this.validateEmail(email)) {
            throw new Error('Invalid email format');
        }

        const userLicenses = this.licenses.filter(l => l.user_email === email);
        
        return {
            email: email,
            total_licenses: userLicenses.length,
            active_licenses: userLicenses.filter(l => l.status === 'active').length,
            licenses: userLicenses.map(l => ({
                id: l.id,
                packages: l.packages,
                status: l.status,
                expires_date: l.expires_date,
                issued_date: l.issued_date
            }))
        };
    }

    // GET /api/download/{licenseId}
    async downloadLicense(licenseId) {
        await this.simulateNetworkDelay(200, 500);
        
        const license = this.licenses.find(l => l.id === licenseId);
        
        if (!license) {
            throw new Error('License not found');
        }

        // Generate encrypted license file content
        const licenseFile = {
            license_id: license.id,
            user_email: license.user_email,
            packages: license.packages,
            features: license.features,
            machine_id: license.machine_id,
            issued_date: license.issued_date,
            expires_date: license.expires_date,
            license_type: license.license_type,
            signature: `qm_sig_${Math.random().toString(36).substring(7)}`,
            encryption: "AES-256-GCM",
            version: "1.0"
        };

        return {
            filename: `${license.packages[0] || 'quantummeta'}_license.qkey`,
            content: JSON.stringify(licenseFile, null, 2),
            content_type: 'application/json'
        };
    }

    // GET /api/analytics
    async getAnalytics() {
        await this.simulateNetworkDelay(300, 800);
        
        // Update real-time stats
        this.analytics.requests_today++;
        this.saveAnalytics();
        
        return this.analytics;
    }

    // Simulate email sending
    async sendLicenseEmail(licenseData) {
        console.log(`[EMAIL SIMULATION] Sending license to ${licenseData.user_email}`);
        console.log(`License ID: ${licenseData.id}`);
        console.log(`Packages: ${licenseData.packages.join(', ')}`);
        
        // In a real implementation, this would use a service like SendGrid, Mailgun, etc.
        return true;
    }

    // Admin endpoints

    // GET /api/admin/licenses
    async getAdminLicenses(adminToken) {
        if (!this.validateAdminToken(adminToken)) {
            throw new Error('Invalid admin token');
        }
        
        await this.simulateNetworkDelay(200, 600);
        return this.licenses;
    }

    // DELETE /api/admin/revoke/{licenseId}
    async revokeLicense(licenseId, adminToken) {
        if (!this.validateAdminToken(adminToken)) {
            throw new Error('Invalid admin token');
        }
        
        await this.simulateNetworkDelay(300, 800);
        
        const licenseIndex = this.licenses.findIndex(l => l.id === licenseId);
        
        if (licenseIndex === -1) {
            throw new Error('License not found');
        }
        
        this.licenses[licenseIndex].status = 'revoked';
        this.saveLicenses();
        
        return {
            success: true,
            message: 'License revoked successfully'
        };
    }

    // Validate admin token (demo implementation)
    validateAdminToken(token) {
        // In production, this would validate against a secure token
        return token === 'qm_admin_2025_secure_token';
    }
}

// Global API instance
window.quantummetaAPI = new LicenseAPI();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LicenseAPI;
}
