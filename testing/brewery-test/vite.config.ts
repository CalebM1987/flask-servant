import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import copy from 'rollup-plugin-copy'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // treat all tags with a dash as custom elements
          isCustomElement: (tag) => tag.includes('calcite-')
        }
      }
    }),
    copy({ // copy over the calcite-components assets
			targets: [
				{
					src: 'node_modules/@esri/calcite-components/dist/calcite/assets/',
					dest: 'public/'
				}
			]
		})
  ]
})
