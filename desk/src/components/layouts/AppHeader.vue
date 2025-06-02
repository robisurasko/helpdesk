<template>
  <div class="flex border-b pr-5">
    <div id="app-header" class="flex-1 w-full flex items-center justify-between">
      <h1 class="text-xl font-semibold">Superapp - Helpdesk</h1>
      <div class="flex items-center space-x-4">
        <div class="relative">
          <select 
            v-model="agentStatus" 
            class="appearance-none bg-gray-100 border border-gray-300 rounded-md px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="updateAgentStatus"
          >
            <option value="Online">Online</option>
            <option value="Busy">Busy</option>
            <option value="Offline">Offline</option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
            <svg class="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
              <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { createResource } from 'frappe-ui';

const agentStatus = ref('Online');
const currentUser = ref('');

// Fetch current user and last status
onMounted(() => {
  // Get current user email
  createResource({
    url: 'frappe.auth.get_logged_user'
  }).submit().then(user => {
    currentUser.value = user;
    
    // Get last status for this user
    createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'HD Agent Activity',
        fields: ['agent_status'],
        filters: { agent_email: user },
        order_by: 'creation desc',
        limit: 1
      }
    }).submit().then(data => {
      if (data && data.length > 0) {
        agentStatus.value = data[0].agent_status;
      }
    });
  });
});

// Update agent status
function updateAgentStatus() {
  createResource({
    url: 'frappe.client.insert',
    params: {
      doc: {
        doctype: 'HD Agent Activity',
        agent_email: currentUser.value,
        agent_status: agentStatus.value,
        created_on: new Date().toISOString()
      }
    }
  }).submit();
}
</script>