<template>
  <div class="flex border-b h-12 items-center">
    <div class="z-20 -mr-4 ml-1 flex items-center justify-center">
      <Button variant="ghosted" @click="sidebarOpened = !sidebarOpened">
        <FeatherIcon name="menu" class="size-4" />
      </Button>
    </div>
    <header id="app-header" class="w-full"></header>
    <!-- Status dropdown moved to its own line -->
      <div class="flex flex-col items-center">
        <div class="flex items-center gap-2">
          <div class="flex items-center gap-1">
            <div class="w-2 h-2 rounded-full" :class="{
              'bg-green-500': agentStatus === 'Online',
              'bg-yellow-500': agentStatus === 'Busy',
              'bg-red-500': agentStatus === 'Offline'
            }"></div>
            
            <div class="relative">
              <select 
                v-model="agentStatus" 
                class="appearance-none bg-gray-100 border border-gray-300 rounded text-xs px-1.5 py-0.5 pr-5 focus:outline-none focus:ring-1 focus:ring-blue-500 h-[1.25rem]"
                @change="updateAgentStatus"
              >
                <option value="Online">Online</option>
                <option value="Busy">Busy</option>
                <option value="Offline">Offline</option>
              </select>
              <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-1 text-gray-500">
                <svg class="fill-current h-2.5 w-2.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
     </div> 
</template>

<script setup>
import { mobileSidebarOpened as sidebarOpened } from "@/composables/mobile";
import { ref, onMounted } from 'vue';
import { createResource } from 'frappe-ui';

const agentStatus = ref('Online');
const currentUser = ref('');
const agentDocName = ref('');

// Load current user and their status
onMounted(() => {
  createResource({
    url: 'frappe.auth.get_logged_user'
  }).submit().then(user => {
    currentUser.value = user;
    
    // Get the agent record for this user
    createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'HD Agent',
        fields: ['name', 'custom_current_status'],
        filters: { name: user },
        limit: 1
      }
    }).submit().then(data => {
      if (data && data.length > 0) {
        agentDocName.value = data[0].name;
        agentStatus.value = data[0].custom_current_status || 'Offline';
      }
    });
  });
});

// Update agent status
function updateAgentStatus() {
  if (!agentDocName.value) return;
  
  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'HD Agent',
      name: agentDocName.value,
      fieldname: 'custom_current_status',
      value: agentStatus.value
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
