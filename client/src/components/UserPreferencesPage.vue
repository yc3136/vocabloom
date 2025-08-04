<template>
  <div class="user-preferences-page">
    <div class="container">
      <h1 class="page-title">User Preferences</h1>
      
      <!-- Profile & Security Section -->
      <div class="section">
        <h2 class="section-title">Account Information</h2>
        <div class="form-grid">
          <div class="info-item">
            <label>Display Name</label>
            <div class="info-text">{{ user?.display_name || 'Not set' }}</div>
          </div>
          <div class="info-item">
            <label>Email Address</label>
            <div class="info-text">{{ user?.email || 'Loading...' }}</div>
          </div>
          <div class="info-item">
            <label>Account Created</label>
            <div class="info-text">{{ user?.created_at ? formatDate(user.created_at) : 'Loading...' }}</div>
          </div>
          <div class="info-item">
            <label>Last Login</label>
            <div class="info-text">{{ user?.last_login_at ? formatDate(user.last_login_at) : 'Never' }}</div>
          </div>
          <div class="info-item button-item">
            <button 
              @click="showDeleteWarning" 
              :disabled="loading"
              class="btn btn-danger"
            >
              Delete Account
            </button>
          </div>
        </div>
        
        <div class="subsection">
          <h3 class="subsection-title">Change Password</h3>
          <div class="form-grid">
            <div class="info-item">
              <label>New Password</label>
              <input 
                v-model="securityForm.newPassword" 
                type="password" 
                placeholder="Enter new password"
                class="form-input"
              />
            </div>
            <div class="info-item">
              <label>Confirm Password</label>
              <input 
                v-model="securityForm.confirmPassword" 
                type="password" 
                placeholder="Confirm new password"
                class="form-input"
              />
            </div>
            <div class="info-item button-item">
              <button 
                @click="changePassword" 
                :disabled="!canChangePassword || loading"
                class="btn btn-primary"
              >
                {{ loading ? 'Changing...' : 'Change Password' }}
              </button>
            </div>
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
            <label>Preferred Languages</label>
            <select 
              v-model="preferencesForm.preferredLanguages" 
              multiple
              class="form-input"
            >
              <option value="Spanish">Spanish</option>
              <option value="French">French</option>
              <option value="German">German</option>
              <option value="Italian">Italian</option>
              <option value="Portuguese">Portuguese</option>
              <option value="Chinese Simplified">Chinese Simplified</option>
              <option value="Japanese">Japanese</option>
              <option value="Korean">Korean</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="actions">
        <button 
          @click="savePreferences" 
          :disabled="loading"
          class="btn btn-primary"
        >
          {{ loading ? 'Saving...' : 'Save Preferences' }}
        </button>
      </div>
    </div>

    <!-- Delete Account Warning Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">⚠️ Delete Account</h3>
        </div>
        <div class="modal-body">
          <p class="warning-text">
            <strong>This action cannot be undone.</strong> Deleting your account will permanently remove:
          </p>
          <ul class="warning-list">
            <li>All your flashcards</li>
            <li>All your translation history</li>
            <li>All your preferences and settings</li>
            <li>Your account data</li>
          </ul>
          <p class="warning-text">
            Are you absolutely sure you want to delete your account?
          </p>
        </div>
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="btn btn-secondary">
            Cancel
          </button>
          <button @click="confirmDeleteAccount" class="btn btn-danger">
            Yes, Delete My Account
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notification';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const loading = ref(false);
const user = ref<any>(null);
const showDeleteModal = ref(false);

// Form data
const securityForm = ref({
  newPassword: '',
  confirmPassword: ''
});

const preferencesForm = ref({
  childName: '',
  childAge: null as number | null,
  preferredLanguages: [] as string[]
});

// Computed properties
const canChangePassword = computed(() => {
  return securityForm.value.newPassword && 
         securityForm.value.confirmPassword && 
         securityForm.value.newPassword === securityForm.value.confirmPassword &&
         securityForm.value.newPassword.length >= 6;
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
    const token = await authStore.getIdToken();
    const response = await fetch('http://127.0.0.1:8000/api/auth/me', {
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
  } catch (error) {
    console.error('Error loading user data:', error);
  }
};

const savePreferences = async () => {
  if (!authStore.isAuthenticated) {
    notificationStore.error('Please log in to save preferences');
    return;
  }

  try {
    loading.value = true;
    const token = await authStore.getIdToken();
    
    const response = await fetch('http://127.0.0.1:8000/api/auth/preferences', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        preferences: {
          child_name: preferencesForm.value.childName,
          child_age: preferencesForm.value.childAge,
          preferred_languages: preferencesForm.value.preferredLanguages,
          content_privacy_default: preferencesForm.value.contentPrivacyDefault
        }
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    notificationStore.success('Preferences saved successfully!');
    
    // Reload user data to get updated preferences
    await loadUserData();
  } catch (error) {
    console.error('Error saving preferences:', error);
    notificationStore.error('Failed to save preferences');
  } finally {
    loading.value = false;
  }
};

const changePassword = async () => {
  if (!securityForm.value.newPassword || !securityForm.value.confirmPassword) {
    notificationStore.error('Please fill in all password fields');
    return;
  }

  if (securityForm.value.newPassword !== securityForm.value.confirmPassword) {
    notificationStore.error('New passwords do not match');
    return;
  }

  try {
    loading.value = true;
    // Note: Password change should be handled by Firebase Auth directly
    // This is a placeholder for future implementation
    notificationStore.info('Password change functionality will be implemented with Firebase Auth');
  } catch (error) {
    console.error('Error changing password:', error);
    notificationStore.error('Failed to change password');
  } finally {
    loading.value = false;
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
    
    const response = await fetch('http://127.0.0.1:8000/api/auth/account', {
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
    }
  } catch (error) {
    console.error('Error deleting account:', error);
    notificationStore.error('Failed to delete account');
  } finally {
    loading.value = false;
  }
};

// Watch for authentication state changes
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated) {
    // Add a small delay to ensure Firebase is fully initialized
    setTimeout(() => {
      loadUserData();
    }, 1000);
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
  background: white;
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

.form-input.disabled {
  background-color: var(--bg-primary);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.button-item {
  display: flex;
  align-items: flex-end;
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
  background: var(--primary-blue-dark);
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
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

.actions {
  padding: 20px 24px;
  text-align: center;
  background: var(--bg-primary);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px 24px 0 24px;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #dc3545;
  margin: 0;
}

.modal-body {
  padding: 20px 24px;
}

.warning-text {
  color: var(--text-primary);
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.warning-list {
  margin: 16px 0;
  padding-left: 20px;
  color: var(--text-primary);
}

.warning-list li {
  margin-bottom: 8px;
  line-height: 1.4;
}

.modal-actions {
  padding: 0 24px 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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

  .modal-content {
    width: 95%;
    margin: 20px;
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
