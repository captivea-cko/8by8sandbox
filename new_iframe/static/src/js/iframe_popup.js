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

        this.$el.hide();
        console.log('Checkpoint');
        console.log(this.$el);

        core.bus.on('toggle_iframe', this, this.toggleIframe);

        //this.call('bus_service', 'onNotification', this, this._onLongpollingNotifications);
    },

    toggleIframe() {
      this.$el.toggle();

    },

});
return IframePopup;

});
