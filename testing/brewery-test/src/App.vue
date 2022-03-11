<script lang="ts">
import { defineAsyncComponent, defineComponent, ref } from 'vue';
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import EventsList from './components/EventsList.vue';
// import MapView from './views/MapView.vue'
const MapView = defineAsyncComponent(()=> import('./views/MapView.vue'))
import '@esri/calcite-components/dist/components/calcite-switch'
import { Switch } from '@esri/calcite-components/dist/types/components/switch/switch'
import { Components } from '@esri/calcite-components/dist/types/components'

export default defineComponent({
  components: {
    MapView,
    EventsList
  },

  setup(){
    const showLoader = ref(true)
    return {
      showLoader,
      onChange(val: boolean){
        console.log('switch changed: ', val)
        showLoader.value = val
      }
    }
  },

  mounted(){
    const calciteSwitch = this.$refs.switch as Switch //Components.CalciteSwitch //
    calciteSwitch.el.addEventListener('calciteSwitchChange', (evt: any)=> {
      this.onChange((evt.target as Switch).checked)
    })
  }
})
</script>

<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-lg-6 col-md-12">
        <calcite-switch :checked="showLoader" 
          @calciteSwitchChange="onChange" 
          label="show loader" ref="switch"
        />
        <p>loader: {{ showLoader }}</p>
        <events-list />
        <!-- <calcite-loader active="true" v-if="showLoader" /> -->
      </div>
      <div class="col-lg-6 col-md-12">
        <Suspense>
          <template #default>
          
            <map-view />
          </template>

          <template #fallback>
          
            <calcite-loader active="true" />
          </template>

        </Suspense>
      </div>

    </div>
  </div>
  
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
