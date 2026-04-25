import { ref } from 'vue'

export function useForm({ validate, submit, onSuccess, successMsg } = {}) {
  const result = ref('')
  const resultType = ref('')
  const loading = ref(false)

  async function doSubmit(...args) {
    result.value = ''
    resultType.value = ''

    if (validate) {
      const err = validate(...args)
      if (err) {
        result.value = err
        resultType.value = 'err'
        return
      }
    }

    loading.value = true
    try {
      const data = await submit(...args)
      if (data.success) {
        result.value = successMsg !== undefined ? successMsg : (data.message || '操作成功')
        resultType.value = 'ok'
        if (onSuccess) onSuccess(data, ...args)
      } else {
        result.value = data.message || '操作失败'
        resultType.value = 'err'
      }
    } catch (e) {
      result.value = e.message || '网络错误'
      resultType.value = 'err'
    } finally {
      loading.value = false
    }
  }

  return { result, resultType, loading, submit: doSubmit }
}
