<script lang="ts">
import { defineComponent, PropType, getCurrentInstance } from "vue";
import { ISocketEvent } from '../types/types';

export default defineComponent({
  name: 'socket-event',
  props: {
    event: {
      type: Object as PropType<ISocketEvent>,
      required: true
    }
  },
  setup(){
    const uid = getCurrentInstance()!.uid
    return {
      uid
    }
  }
})
</script>

<template>

  <li :class="`list-group-item event-info my-1 ${event.theme ? 'list-group-item-' + event.theme: ''}`">
    <div class="d-flex justify-content-between">
      <h5 class="card-title">{{event.type }}: {{event.name}}</h5>
      <span></span>
    </div>
    <p class="text-secondary text-sm">{{ event.time }}</p>
    <button class="btn btn-primary" type="button" data-toggle="collapse" :data-target="`#event-payload-${uid}`" aria-expanded="false" aria-controls="collapseExample">
      Show Payload
    </button>
    <div class="payload-content collapse" :id="`event-payload-${uid}`">
      <div class="card card-body">
        <textarea cols="30" rows="10" readonly>
          {{ JSON.stringify(event.payload, null, 2).trimStart() }}
        </textarea>
      </div>
    </div>
  </li>

</template>

<style>
  .event-info {
    min-width: 400px;
  }

</style>