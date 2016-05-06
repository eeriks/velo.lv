window.ENV = window.ENV || {}

@format_date = (dt) ->
  month = if dt.getUTCMonth() > 8 then "#{dt.getUTCMonth() + 1}"  else "0#{dt.getUTCMonth() + 1}"
  date = if dt.getUTCDate() > 9 then "#{dt.getUTCDate()}"  else "0#{dt.getUTCDate()}"
  hours = if dt.getUTCHours() > 9 then "#{dt.getUTCHours()}"  else "0#{dt.getUTCHours()}"
  minutes = if dt.getUTCMinutes() > 9 then "#{dt.getUTCMinutes()}"  else "0#{dt.getUTCMinutes()}"
  "#{ dt.getUTCFullYear() }-#{ month }-#{ date } #{ hours }:#{ minutes }"


call_formset_function = (row, container, type) ->
  function_name = field for field in $(container).prop("class").split(' ') when field.indexOf('_inline_class') != -1
  if window.console
    console.log function_name+'_'+type
  if typeof window[function_name+'_'+type] == 'function'
    window[function_name+'_'+type](row)

formset = (containers) ->
  ret_obj = {}
  for container in containers

    prefix = $(container).data "prefix"
    $container = $(container).find(".formset_container")
    $items = $container.find ".item:not(.template)"
    $items.formset
      prefix: prefix
      container: $container
      addText: ''
      addCssClass: 'add-new-row'
      addCssSelector: '.add-new-row'
      deleteButtonSelector: '.delete_button'
      deleteText: ''
      deleteCssClass: ''
      upCssClass: 'btn btn-sm icon-arrow-up'
      downCssClass: 'btn btn-sm icon-arrow-down'
      formTemplate: $(container).parent().find ".template"
      added: (row) -> call_formset_function(row, container, 'added')
      removed: (row) -> call_formset_function(row, container, 'removed')


$ ->
  window.ENV.formsets = formset $ '.django-inline-form'