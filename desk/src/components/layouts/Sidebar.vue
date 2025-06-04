<template>
  <div
    class="z-0 flex select-none flex-col border-r border-gray-200 bg-gray-50 p-2 text-base duration-300 ease-in-out"
    :style="{
      'min-width': width,
      'max-width': width,
    }"
  > <!-- Status dropdown aligned left -->
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

    <UserMenu class="mb-2 ml-0.5" :options="profileSettings" />
    <SidebarLink
      v-if="!isCustomerPortal"
      label="Search"
      class="mb-1"
      :icon="LucideSearch"
      :on-click="() => openCommandPalette()"
      :is-expanded="isExpanded"
    >
      <template #right>
        <span class="flex items-center gap-0.5 font-medium text-gray-600">
          <component :is="device.modifierIcon" class="h-3 w-3" />
          <span>K</span>
        </span>
      </template>
    </SidebarLink>
    <div class="mb-4" v-if="!isCustomerPortal">
      <div
        v-if="notificationStore.unread"
        class="absolute z-20 h-1.5 w-1.5 translate-x-6 translate-y-1 rounded-full bg-blue-400 left-1"
        theme="gray"
        variant="solid"
      />
      <SidebarLink
        class="relative"
        label="Notifications"
        :icon="LucideBell"
        :on-click="() => notificationStore.toggle()"
        :is-expanded="isExpanded"
      >
        <template #right>
          <Badge
            v-if="isExpanded && notificationStore.unread"
            :label="
              notificationStore.unread > 9 ? '9+' : notificationStore.unread
            "
            theme="gray"
            variant="subtle"
          />
        </template>
      </SidebarLink>
    </div>
    <div class="overflow-y-auto">
      <div v-for="view in allViews" :key="view.label">
        <div
          v-if="!view.hideLabel && !isExpanded && view.views?.length"
          class="mx-2 my-2 h-1"
        />
        <Section
          :label="view.label"
          :hideLabel="view.hideLabel"
          :opened="view.opened"
        >
          <template #header="{ opened, hide, toggle }">
            <div
              v-if="!hide"
              class="flex cursor-pointer gap-1.5 px-1 text-base font-medium text-ink-gray-5 transition-all duration-300 ease-in-out"
              :class="
                !isExpanded
                  ? 'ml-0 h-0 overflow-hidden opacity-0'
                  : 'mt-4 h-7 w-auto opacity-100'
              "
              @click="toggle()"
            >
              <FeatherIcon
                name="chevron-right"
                class="h-4 text-ink-gray-9 transition-all duration-300 ease-in-out"
                :class="{ 'rotate-90': opened }"
              />
              <span>{{ view.label }}</span>
            </div>
          </template>
          <nav class="flex flex-col">
            <SidebarLink
              v-for="link in view.views"
              :icon="link.icon"
              :label="link.label"
              :to="link.to"
              :key="link.label"
              :is-expanded="isExpanded"
              :is-active="isActiveTab(link.to)"
              class="my-0.5 emoji"
              :onClick="link.onClick"
            />
          </nav>
        </Section>
      </div>
    </div>
    <div class="grow" />
    <TrialBanner
      v-if="isFCSite && !isCustomerPortal"
      :isSidebarCollapsed="!isExpanded"
    />
    <SidebarLink
      :icon="isExpanded ? LucideArrowLeftFromLine : LucideArrowRightFromLine"
      :is-active="false"
      :is-expanded="isExpanded"
      :label="isExpanded ? 'Collapse' : 'Expand'"
      :on-click="() => (isExpanded = !isExpanded)"
    />
    <SettingsModal v-model="showSettingsModal" />
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { TrialBanner } from "frappe-ui/frappe";
import { storeToRefs } from "pinia";
import { useAuthStore } from "@/stores/auth";
import { useNotificationStore } from "@/stores/notification";
import { useSidebarStore } from "@/stores/sidebar";
import { CUSTOMER_PORTAL_LANDING } from "@/router";
import { useDevice } from "@/composables";
import { SidebarLink } from "@/components";
import UserMenu from "@/components/UserMenu.vue";
import LucideArrowLeftFromLine from "~icons/lucide/arrow-left-from-line";
import LucideArrowRightFromLine from "~icons/lucide/arrow-right-from-line";
import LucideBell from "~icons/lucide/bell";
import LucideSearch from "~icons/lucide/search";
import SettingsModal from "@/components/Settings/SettingsModal.vue";
import Apps from "@/components/Apps.vue";
import { isCustomerPortal } from "@/utils";
import {
  agentPortalSidebarOptions,
  customerPortalSidebarOptions,
} from "./layoutSettings";
import { Section } from "@/components";
import { useView, currentView } from "@/composables/useView";
import { FrappeCloudIcon } from "@/components/icons";
import { confirmLoginToFrappeCloud } from "@/composables/fc";
import { useScreenSize } from "@/composables/screen";
const { isMobileView } = useScreenSize();

//import for dropdown status agent - rnd;
import { createResource } from 'frappe-ui';

//status agent function - rnd
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
        fields: ['name', 'custom_current_status'],  // Changed to custom_current_status
        filters: { name: user },
        limit: 1
      }
    }).submit().then(data => {
      if (data && data.length > 0) {
        agentDocName.value = data[0].name;
        agentStatus.value = data[0].custom_current_status || 'Offline';  // Changed to custom_current_status
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
      fieldname: 'custom_current_status',  // Changed to custom_current_status
      value: agentStatus.value
    }
  }).submit();
}


//original helpdesk
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const { isExpanded, width } = storeToRefs(useSidebarStore());
const device = useDevice();
const showSettingsModal = ref(false);

const { pinnedViews, publicViews } = useView();

declare global {
  interface Window {
    is_fc_site: boolean;
  }
}
const isFCSite = ref(window.is_fc_site);

const allViews = computed(() => {
  const items = isCustomerPortal.value
    ? customerPortalSidebarOptions
    : agentPortalSidebarOptions;

  const options = [
    {
      label: "All Views",
      hideLabel: true,
      opened: true,
      views: items,
    },
  ];
  if (publicViews.value?.length && !isCustomerPortal.value) {
    options.push({
      label: "Public Views",
      opened: true,
      hideLabel: false,
      views: parseViews(publicViews.value),
    });
  }
  if (pinnedViews.value?.length) {
    options.push({
      label: "Private Views",
      opened: true,
      hideLabel: false,
      views: parseViews(pinnedViews.value),
    });
  }
  return options;
});

function parseViews(views) {
  return views.map((view) => {
    return {
      label: view.label,
      icon: view.icon,
      to: {
        name: view.route_name,
        query: { view: view.name },
      },
      onClick: () => {
        currentView.value = {
          label: view.label,
          icon: view.icon,
        };
      },
    };
  });
}

const customerPortalDropdown = computed(() => [
  {
    label: "Log out",
    icon: "log-out",
    onClick: () => authStore.logout(),
  },
]);

const agentPortalDropdown = computed(() => [
  {
    component: markRaw(Apps),
  },
  {
    label: "Customer portal",
    icon: "users",
    onClick: () => {
      const path = router.resolve({ name: CUSTOMER_PORTAL_LANDING });
      window.open(path.href);
    },
  },
  {
    icon: "life-buoy",
    label: "Support",
    onClick: () => window.open("https://t.me/frappedesk"),
  },
  {
    icon: "book-open",
    label: "Docs",
    onClick: () => window.open("https://docs.frappe.io/helpdesk"),
  },
  {
    label: "Login to Frappe Cloud",
    icon: FrappeCloudIcon,
    onClick: () => confirmLoginToFrappeCloud(),
    condition: () => !isMobileView.value && window.is_fc_site,
  },
  {
    label: "Settings",
    icon: "settings",
    onClick: () => (showSettingsModal.value = true),
    condition: () => authStore.isAdmin || authStore.isManager,
  },
  {
    label: "Log out",
    icon: "log-out",
    onClick: () => authStore.logout(),
  },
]);

const profileSettings = computed(() => {
  return isCustomerPortal.value
    ? customerPortalDropdown.value
    : agentPortalDropdown.value;
});

function isActiveTab(to: any) {
  if (route.query.view) {
    return route.query.view == to?.query?.view;
  }
  return route.name === to;
}

function openCommandPalette() {
  window.dispatchEvent(
    new KeyboardEvent("keydown", { key: "k", metaKey: true })
  );
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