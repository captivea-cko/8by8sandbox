odoo.define('iframe_webclient', function (require) {
"use strict";

const IframePopup = require('iframe_popup');

const config = require('web.config');
const WebClient = require('web.WebClient');

// As voip is not supported on mobile devices,
// we want to keep the standard phone widget
if (config.device.isMobile) {
    return;
}

WebClient.include({

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async show_application() {
        await this._super(...arguments);
        this._iframe = new IframePopup(this);
        await this._iframe.appendTo(this.$el);
        alert('Webclient loaded and iframe added')
    },

});
});
