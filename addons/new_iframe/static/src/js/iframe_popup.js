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
        this.$el.find('iframe')
          .first()
          // TODO change to dynamic link settings
          .attr('src', 'https://cloud8-staging.8x8.com/mapanelweb/public/index.html?companel=vo&env=oneinn&fullContext=false')

        core.bus.on('toggle_iframe', this, this.toggleIframe);

        //this.call('bus_service', 'onNotification', this, this._onLongpollingNotifications);
    },

    toggleIframe() {
      this.$el.toggle();

    },

});
return IframePopup;

});
