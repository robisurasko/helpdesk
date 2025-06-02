<template>
  <div class="flex border-b pr-5">
    <div id="app-header" class="flex-1 w-full flex items-center justify-center">
      <!-- Centered status dropdown -->
      <div class="flex items-center">
        <div class="w-2 h-2 rounded-full mr-1.5" :class="{
          'bg-green-500': agentStatus === 'Online',
          'bg-yellow-500': agentStatus === 'Busy',
          'bg-red-500': agentStatus === 'Offline'
        }"></div>
        
        <div class="relative">
          <select 
            v-model="agentStatus" 
            class="appearance-none bg-gray-100 border border-gray-300 rounded-md px-2 py-1 pr-6 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            @change="updateAgentStatus"
          >
            <option value="Online">Online</option>
            <option value="Busy">Busy</option>
            <option value="Offline">Offline</option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-1 text-gray-700">
            <svg class="fill-current h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
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

function getCurrentDateTime() {
  const now = new Date();
  return now.toISOString().slice(0, 19).replace('T', ' ');
}

onMounted(() => {
  createResource({
    url: 'frappe.auth.get_logged_user'
  }).submit().then(user => {
    currentUser.value = user;
    
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

function updateAgentStatus() {
  createResource({
    url: 'frappe.client.insert',
    params: {
      doc: {
        doctype: 'HD Agent Activity',
        agent_email: currentUser.value,
        agent_status: agentStatus.value,
        created_on: getCurrentDateTime()
      }
    }
  }).submit();
}
</script>

<style scoped>
select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-image: none;
}
</style>