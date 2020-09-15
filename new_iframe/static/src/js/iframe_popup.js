odoo.define('iframe_popup', function (require) {
"use strict";


const core = require('web.core');
const config = require('web.config');
const realSession = require('web.session');
const Widget = require('web.Widget');

const IframePopup = Widget.extend({
    template: 'iframe_popup',
    events: {  },
    /**
     * @constructor
     */
    init() {
      this._isClosed = true;
    },
    /**
     * @override
     */
    async start() {

        this.$el.css('bottom', 0);
        this.$el.show();

        core.bus.on('toggle_iframe', this, this.toggleIframe);

        this.call('bus_service', 'onNotification', this, this._onLongpollingNotifications);
    },

    toggleIframe() {
      if (this._isClosed) {
        this.$el.show();
        this._isClosed = false;
      }
      else {
        this.$el.hide();
        this._isClosed = true;
      }

    },

});

return IframePopup;

});
