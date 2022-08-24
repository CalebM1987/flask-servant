<script setup lang="ts">
import { Feature } from 'geojson'
import { PropType, computed } from 'vue'

export interface IFeaturePopupProps {
  feature: Feature;
  fields?: string[];
}

const props = defineProps({
  feature: {
    type: Object as PropType<Feature>,
    required: true
  },
  fields: {
    type: Array as PropType<string[]>,
    default(){
      return []
    }
  }
})

const rows = computed(()=> {
  const ftProps = props.feature.properties ?? {}
  const fields: string[] = props.fields.length 
    ? props.fields
    : Object.keys(ftProps)
  
  return fields.map(f => { 
    return {
        label: f,
        value: ftProps[f]
      }
    }
  )
  
})
</script>

<template>
<div class="feature-popup">
  <table v-if="feature">
    <table class="table">
      <tr v-for="row in rows">
        <td>{{ row.label }}</td>
        <td>{{row.value }}</td>
      </tr>
    </table>
  </table>

</div>
</template> 