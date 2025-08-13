<template>
  <div class="user-preferences-page">
    <div class="container">
      
      <!-- Profile & Security Section -->
      <div class="section">
        <h2 class="section-title">Account Information</h2>
        <div class="form-grid">
          <div class="info-item">
            <label>Email Address</label>
            <div class="info-text">{{ user?.email || 'Loading...' }}</div>
          </div>
          <div class="info-item">
            <label>Email Verification</label>
            <div class="info-text">
              <span v-if="authStore.user?.emailVerified" class="verified-badge">
                ✅ Verified
              </span>
              <span v-else class="unverified-badge">
                ❌ Not Verified
                <button 
                  @click="resendVerification" 
                  :disabled="authStore.loading"
                  class="resend-btn"
                >
                  {{ authStore.loading ? 'Sending...' : 'Resend Email' }}
                </button>
              </span>
            </div>
          </div>
          <div class="info-item">
            <label>Account Created</label>
            <div class="info-text">{{ user?.created_at ? formatDate(user.created_at) : 'Loading...' }}</div>
          </div>
          <div class="info-item">
            <label>Last Login</label>
            <div class="info-text">{{ user?.last_login_at ? formatDate(user.last_login_at) : (user ? 'Never' : 'Loading...') }}</div>
          </div>
        </div>
        <div class="section-actions">
          <button 
            @click="showDeleteWarning" 
            :disabled="loading"
            class="btn btn-danger"
          >
            Delete Account
          </button>
        </div>
        
        <div class="subsection">
          <h3 class="subsection-title">Change Password</h3>
          <div class="form-grid">
            <div class="info-item">
              <label>Current Password</label>
              <div class="password-input-container">
                <input 
                  v-model="securityForm.currentPassword" 
                  :type="showCurrentPassword ? 'text' : 'password'"
                  placeholder="Enter your current password"
                  class="form-input password-input"
                />
                <button 
                  type="button"
                  @click="showCurrentPassword = !showCurrentPassword"
                  class="password-toggle-btn"
                  :title="showCurrentPassword ? 'Hide password' : 'Show password'"
                >
                  {{ showCurrentPassword ? '🙈' : '👁️' }}
                </button>
              </div>
            </div>
            <div class="info-item">
              <label>New Password</label>
              <div class="password-input-container">
                <input 
                  v-model="securityForm.newPassword" 
                  :type="showNewPassword ? 'text' : 'password'"
                  placeholder="Enter new password (min 6 characters)"
                  class="form-input password-input"
                  :class="{ 'error': passwordErrors.length > 0, 'success': canChangePassword }"
                />
                <button 
                  type="button"
                  @click="showNewPassword = !showNewPassword"
                  class="password-toggle-btn"
                  :title="showNewPassword ? 'Hide password' : 'Show password'"
                >
                  {{ showNewPassword ? '🙈' : '👁️' }}
                </button>
              </div>
              <div v-if="passwordErrors.length > 0" class="validation-errors">
                <div v-for="error in passwordErrors" :key="error" class="error-message">
                  {{ error }}
                </div>
              </div>
            </div>
            <div class="info-item">
              <label>Confirm Password</label>
              <div class="password-input-container">
                <input 
                  v-model="securityForm.confirmPassword" 
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="Confirm new password"
                  class="form-input password-input"
                  :class="{ 'error': passwordErrors.length > 0, 'success': canChangePassword }"
                />
                <button 
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="password-toggle-btn"
                  :title="showConfirmPassword ? 'Hide password' : 'Show password'"
                >
                  {{ showConfirmPassword ? '🙈' : '👁️' }}
                </button>
              </div>
              <div v-if="canChangePassword" class="validation-success">
                <div class="success-message">✅ Password requirements met</div>
              </div>
            </div>
          </div>
          <div class="section-actions">
            <button 
              @click="changePassword" 
              :disabled="!canChangePassword || authStore.loading"
              class="btn btn-primary"
            >
              {{ authStore.loading ? 'Changing...' : 'Change Password' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Preferences Section -->
      <div class="section">
        <h2 class="section-title">Learning Preferences</h2>
        <p class="section-description">
          Help personalize your learning experience by providing information about your child.
        </p>
        <div class="form-grid">
          <div class="info-item">
            <label>Child's Name</label>
            <input 
              v-model="preferencesForm.childName" 
              type="text" 
              placeholder="Enter child's name"
              class="form-input"
            />
          </div>
          <div class="info-item">
            <label>Child's Age</label>
            <input 
              v-model.number="preferencesForm.childAge" 
              type="number" 
              min="1" 
              max="18"
              placeholder="Age"
              class="form-input"
            />
          </div>
          <div class="info-item">
            <label>Primary Preferred Language</label>
            <select 
              v-model="preferencesForm.primaryLanguage" 
              class="language-select"
            >
              <option v-for="lang in languages" :key="lang.value" :value="lang.value">
                {{ lang.label }}
              </option>
            </select>
          </div>
        </div>
        <div class="section-actions">
          <button 
            @click="saveLearningPreferences" 
            :disabled="loading"
            class="btn btn-primary"
          >
            {{ loading ? 'Saving...' : 'Save Learning Preferences' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Account Confirmation Modal -->
    <ConfirmationModal
      :show="showDeleteModal"
      title="Delete Account"
      message="This action cannot be undone. Deleting your account will permanently remove all your flashcards, translation history, preferences, and account data."
      details="Are you absolutely sure you want to delete your account?"
      type="danger"
      confirm-text="Yes, Delete My Account"
      cancel-text="Cancel"
      :loading="loading"
      @confirm="confirmDeleteAccount"
      @cancel="closeDeleteModal"
      @close="closeDeleteModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notification';
import { usePreferencesStore } from '../stores/preferences';
import { SUPPORTED_LANGUAGES } from '../constants/languages';
import ConfirmationModal from './ConfirmationModal.vue';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const preferencesStore = usePreferencesStore();
const router = useRouter();

const loading = ref(false);
const user = ref<any>(null);
const showDeleteModal = ref(false);

// Password visibility states
const showCurrentPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

// Form data
const securityForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const preferencesForm = ref({
  childName: '',
  childAge: null as number | null,
  primaryLanguage: 'Chinese' as string
});

// Use the shared language constants
const languages = SUPPORTED_LANGUAGES;

// Computed properties
const canChangePassword = computed(() => {
  return securityForm.value.currentPassword &&
         securityForm.value.newPassword && 
         securityForm.value.confirmPassword && 
         securityForm.value.newPassword === securityForm.value.confirmPassword &&
         securityForm.value.newPassword.length >= 6;
});

const passwordErrors = computed(() => {
  const errors = [];
  
  if (securityForm.value.currentPassword || securityForm.value.newPassword || securityForm.value.confirmPassword) {
    if (!securityForm.value.currentPassword) {
      errors.push('Current password is required');
    }
    
    if (!securityForm.value.newPassword) {
      errors.push('New password is required');
    } else if (securityForm.value.newPassword.length < 6) {
      errors.push('Password must be at least 6 characters long');
    }
    
    if (!securityForm.value.confirmPassword) {
      errors.push('Please confirm your password');
    } else if (securityForm.value.newPassword !== securityForm.value.confirmPassword) {
      errors.push('Passwords do not match');
    }
  }
  
  return errors;
});

// Methods
const formatDate = (dateString: string | undefined) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString();
};

const loadUserData = async () => {
  if (!authStore.isAuthenticated || !authStore.isFirebaseConfigured) {
    return;
  }

  try {
    // Load user data and preferences
    await preferencesStore.loadPreferences();
    
    const token = await authStore.getIdToken();
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
    const response = await fetch(`${API_BASE}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const userData = await response.json();
    user.value = userData;
    
    // Populate the form with current preferences
    if (preferencesStore.preferences) {
      preferencesForm.value.childName = preferencesStore.preferences.child_name || '';
      preferencesForm.value.childAge = preferencesStore.preferences.child_age || null;
      preferencesForm.value.primaryLanguage = preferencesStore.preferences.preferred_languages?.[0] || 'Chinese';
    }
  } catch (error) {
    console.error('Error loading user data:', error);
  }
};

const saveLearningPreferences = async () => {
  if (!authStore.isAuthenticated) {
    notificationStore.error('Please log in to save preferences');
    return;
  }

  try {
    loading.value = true;
    
    await preferencesStore.savePreferences({
      child_name: preferencesForm.value.childName || undefined,
      child_age: preferencesForm.value.childAge || undefined,
      preferred_languages: [preferencesForm.value.primaryLanguage]
    });

    notificationStore.success('Learning preferences saved successfully!');
    
    // Reload user data to get updated preferences
    await loadUserData();
  } catch (error) {
    console.error('Error saving learning preferences:', error);
    notificationStore.error('Failed to save learning preferences');
  } finally {
    loading.value = false;
  }
};

const changePassword = async () => {
  if (!securityForm.value.currentPassword || !securityForm.value.newPassword || !securityForm.value.confirmPassword) {
    notificationStore.error('Please fill in all password fields');
    return;
  }

  if (securityForm.value.newPassword !== securityForm.value.confirmPassword) {
    notificationStore.error('New passwords do not match');
    return;
  }

  if (securityForm.value.newPassword.length < 6) {
    notificationStore.error('Password must be at least 6 characters long');
    return;
  }

  try {
    await authStore.changePassword(securityForm.value.newPassword, securityForm.value.currentPassword);
    // Clear the form after successful password change
    securityForm.value.currentPassword = '';
    securityForm.value.newPassword = '';
    securityForm.value.confirmPassword = '';
  } catch (error) {
    console.error('Error changing password:', error);
    // Error is already handled by the auth store
  }
};

const showDeleteWarning = () => {
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const confirmDeleteAccount = async () => {
  if (!authStore.isAuthenticated) {
    notificationStore.error('Please log in to delete your account');
    return;
  }

  try {
    loading.value = true;
    const token = await authStore.getIdToken();
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
    
    const response = await fetch(`${API_BASE}/api/auth/account`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        confirm_email: user.value?.email
      })
    });

    if (!response.ok) {
      if (response.status === 401) {
        notificationStore.error('Please log in to delete your account');
      } else {
        const error = await response.json();
        notificationStore.error(error.detail || 'Failed to delete account');
      }
    } else {
      notificationStore.success('Account deleted successfully');
      closeDeleteModal();
      await authStore.logout();
      // Redirect to home page after account deletion
      router.push('/');
    }
  } catch (error) {
    console.error('Error deleting account:', error);
    notificationStore.error('Failed to delete account');
  } finally {
    loading.value = false;
  }
};

const resendVerification = async () => {
  try {
    await authStore.resendEmailVerification();
  } catch (error) {
    console.error('Error resending verification:', error);
    // Error is already handled by the auth store
  }
};

// Watch for authentication state changes
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated) {
    // Add a small delay to ensure Firebase is fully initialized
    setTimeout(() => {
      loadUserData();
    }, 1000);
  } else {
    // User is no longer authenticated, redirect to home
    router.push('/');
  }
});

// Load user data on component mount
onMounted(() => {
  if (authStore.isAuthenticated) {
    // Add a small delay to ensure Firebase is fully initialized
    setTimeout(() => {
      loadUserData();
    }, 1000);
  }
});
</script>

<style scoped>
.user-preferences-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 16px;
}

.container {
  background: var(--bg-surface);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 24px 0;
  padding: 24px 24px 0 24px;
}

.section {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.section-description {
  color: var(--text-secondary);
  margin: 0 0 16px 0;
  line-height: 1.4;
  font-size: 14px;
}

.info-item {
  margin-bottom: 16px;
}

.info-item label {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
  font-size: 14px;
}

.info-text {
  padding: 10px 0;
  font-size: 14px;
  color: var(--text-primary);
  min-height: 20px;
  display: flex;
  align-items: center;
  font-weight: 500;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.subsection {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.subsection-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
}

.form-input.error {
  border-color: var(--error-red);
}

.form-input.success {
  border-color: var(--success-green);
}

.form-input.disabled {
  background-color: var(--bg-primary);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.language-select {
  width: 100%;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  font-size: 14px;
  background: var(--bg-surface, #ffffff);
  color: var(--text-primary, #1e293b);
  cursor: pointer;
  transition: border-color 0.2s;
}

.language-select:focus {
  outline: none;
  border-color: var(--primary-blue);
}

.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input {
  padding-right: 40px; /* Make room for the toggle button */
}

.password-toggle-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  font-size: 16px;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.password-toggle-btn:hover {
  color: var(--text-primary);
  background: var(--bg-primary);
}

.validation-errors {
  margin-top: 8px;
}

.validation-errors .error-message {
  color: var(--error-red);
  font-size: 12px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.validation-errors .error-message:before {
  content: "⚠️";
  margin-right: 4px;
  font-size: 10px;
}

.validation-success {
  margin-top: 8px;
}

.validation-success .success-message {
  color: var(--success-green);
  font-size: 12px;
  font-weight: 500;
}

.verified-badge {
  color: var(--success-green);
  font-weight: 500;
}

.unverified-badge {
  color: var(--error-red);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 12px;
}

.resend-btn {
  background: var(--primary-blue);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.resend-btn:hover:not(:disabled) {
  background: var(--blue-hover);
}

.resend-btn:disabled {
  background: var(--text-secondary);
  cursor: not-allowed;
}

.button-item {
  display: flex;
  align-items: flex-end;
}

.section-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-start;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--blue-hover);
}

.btn-secondary {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--border-color);
}

.btn-danger {
  background: var(--error-red);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: var(--error-red);
  opacity: 0.8;
}





@media (max-width: 768px) {
  .user-preferences-page {
    padding: 12px;
  }
  
  .section {
    padding: 20px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .button-item {
    margin-top: 8px;
  }


}
</style>
