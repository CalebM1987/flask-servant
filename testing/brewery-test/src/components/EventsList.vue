<script lang="ts">
import { defineComponent, defineAsyncComponent, ref, Ref, onMounted } from "vue";
const SocketEvent = defineAsyncComponent(()=> import('./SocketEvent.vue'))
import { ISocketEvent } from "../types/types";
import { handleSocket } from '../util/util'
import { socket } from '../services/api'

export default defineComponent({
  name: 'events-list',
  components: {
    SocketEvent
  },

  setup(){
    const events: Ref<ISocketEvent[]> = ref([])

    onMounted(async ()=> {
      
      console.log('setting up websocket: ', socket)
      for (const table of ['brewery', 'beer', 'style', 'category']){
        for (const op of ['find', 'create', 'patch', 'delete']){
          const eventName = `${table}/${op}`
          socket.on(eventName, (payload)=> {
            console.log(eventName, payload)
            const event = handleSocket(socket, eventName, payload)
            events.value.unshift(event)
            setTimeout(()=> events.value.pop(), 120000)
          })
        }
      }
    })

    return {
      events
    }
  }
})

</script>

<template>
  <div class="event-list">
    <h3>WebSocket Events</h3>
    <ul class="list-group">
      <socket-event 
        v-for="(event,i) in events" 
        :event="event" 
        :key="i"
      ></socket-event>
    </ul>
  </div>

</template>

<style>
  .event-list {
    min-height: 400px;
  }
</style>