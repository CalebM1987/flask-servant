import { createApp } from 'vue'
import App from './App.vue'
import VueMapboxTs from "vue-mapbox-ts";
import PrimeVue from 'primevue/config';
import { setAssetPath } from '@esri/calcite-components/dist/components';
import "@esri/calcite-components/dist/components/calcite-button";
import "@esri/calcite-components/dist/components/calcite-icon";
import "@esri/calcite-components/dist/components/calcite-loader";
import '@esri/calcite-components/dist/calcite/calcite.css';
import ToastService from 'primevue/toastservice';
console.log('TOAST SERVICE: ', ToastService)
import 'primevue/resources/themes/saga-blue/theme.css'       //theme
import 'primevue/resources/primevue.min.css'                 //core css
import 'primeicons/primeicons.css'

setAssetPath(location.href);

// Local assets
// setAssetPath(PATH); // PATH depends on framework, more info below

createApp(App)
    .use(VueMapboxTs)
    .use(PrimeVue)
    .use(ToastService)
    .mount('#app')



