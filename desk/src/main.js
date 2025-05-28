import { createApp } from "vue";
import { createPinia } from "pinia";
import {
  frappeRequest,
  resourcesPlugin,
  setConfig,
  Badge,
  Button,
  Dialog,
  ErrorMessage,
  FeatherIcon,
  FormControl,
  Input,
  Tooltip,
  TextInput,
} from "frappe-ui";
import App from "./App.vue";
import "./index.css";
import { router } from "./router";
import { socket } from "./socket";
import { createToast } from "@/utils";
import { posthogPlugin } from "./telemetry";
import { createDialog } from "./components/dialogs";

const globalComponents = {
  Badge,
  Button,
  Dialog,
  ErrorMessage,
  FeatherIcon,
  FormControl,
  Input,
  Tooltip,
  TextInput,
};

setConfig("resourceFetcher", frappeRequest);
setConfig("fallbackErrorHandler", (error) => {
  const text = error.exc_type
    ? (error.messages || error.message || []).join(", ")
    : error.message;
  createToast({
    title: error.exc_type || "Error",
    text,
    icon: "alert-triangle",
    iconClasses: "text-red-500",
  });
});

const pinia = createPinia();
const app = createApp(App);

app.use(resourcesPlugin);
app.use(pinia);
app.use(router);
app.use(posthogPlugin);
for (const c in globalComponents) {
  app.component(c, globalComponents[c]);
}

app.config.globalProperties.$socket = socket;
app.config.globalProperties.$toast = createToast;
app.config.globalProperties.$dialog = createDialog;

if (import.meta.env.DEV) {
  frappeRequest({
    url: "/api/method/helpdesk.www.helpdesk.index.get_context_for_dev",
  }).then((values) => {
    for (let key in values) {
      window[key] = values[key];
    }
    app.mount("#app");
  });
} else {
  app.mount("#app");
}
