odoo.define('iframe_popup', function (require) {
  "use strict";


  const core = require('web.core');
  const config = require('web.config');
  const realSession = require('web.session');
  const Widget = require('web.Widget');

  // As voip is not supported on mobile devices,
  // we want to keep the standard phone widget
  if (config.device.isMobile) {
    return;
  }

  const IframePopup = Widget.extend({
    template: 'iframe_popup',
    events: {  },

    /**
    * @constructor
    */
    init() {
      this._super(...arguments);

    },
    /**
    * @override
    */
    async start() {
      console.log(realSession);
      this.$el.hide();
      this.$el.find('iframe')
      .first()
      // TODO change to dynamic link settings
      .attr('src', 'https://cloud8-staging.8x8.com/mapanelweb/public/index.html?companel=vo&env=odoo&instanceUrl=' + realSession.origin)

      core.bus.on('toggle_iframe', this, this.toggleIframe);

      this.$el.find('.o_popup_btn_close').first().on('click', () => core.bus.trigger('toggle_iframe'))

      var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
      this.$el.on('mousedown', dragMouseDown);

      var drgElem = this.$el;

      function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        $(document).on('mouseup', () => {
          $(document).unbind('mouseup');
          $(document).unbind('mousemove');
        });
        // call a function whenever the cursor moves:
        $(document).on('mousemove', elementDrag);
      }

      function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        drgElem.css('top', (drgElem.offset().top - pos2) + "px");
        drgElem.css('left', (drgElem.offset().left - pos1) + "px");
      }

      function closeDragElement() {
        // stop moving when mouse button is released:
        $(document).on('mouseup', null);
        $(document).on('mousemove', null);
      }

      //this.call('bus_service', 'onNotification', this, this._onLongpollingNotifications);
    },

    toggleIframe() {
      this.$el.toggle();
    },

  });
  return IframePopup;

});
