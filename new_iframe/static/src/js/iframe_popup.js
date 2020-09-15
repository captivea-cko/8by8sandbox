odoo.define('iframe_popup', function (require) {
"use strict";


const core = require('web.core');
const config = require('web.config');
const realSession = require('web.session');
const Widget = require('web.Widget');

const IframePopup = Widget.extend({
    template: 'iframe_popup',
    events: {  },

    async start() {

        this.$el.hide();

        core.bus.on('toggle_iframe', this, this.toggleIframe);

        //this.call('bus_service', 'onNotification', this, this._onLongpollingNotifications);
    },

    toggleIframe() {
      this.$el.toggle();

    },

});
return IframePopup;

});
