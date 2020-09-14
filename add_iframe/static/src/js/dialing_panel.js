odoo.define('voip.DialingPanel', function (require) {
"use strict";

const core = require('web.core');
const config = require('web.config');
const realSession = require('web.session');
const Widget = require('web.Widget');

const _t = core._t;
const HEIGHT_OPEN = '480px';
const HEIGHT_FOLDED = '0px';

// As voip is not supported on mobile devices,
// we want to keep the standard phone widget
if (config.device.isMobile) {
    return;
}

const DialingPanel = Widget.extend({
    template: 'voip.DialingPanel',

    /**
     * @constructor
     */
    init() {
        this._super(...arguments);

        this.title = _t("iFrame");

        this._isFolded = false;
        this._isInCall = false;
        this._isPostpone = false;
        this._isShow = false;
        this._isWebRTCSupport = window.RTCPeerConnection && window.MediaStream && navigator.mediaDevices;

    },
    /**
     * @override
     */
    async start() {
        this.$el.css('bottom', 0);
        this.$el.hide();

        core.bus.on('transfer_call', this, this._onTransferCall);
        core.bus.on('voip_onToggleDisplay', this, this._onToggleDisplay);
      },
      async _toggleDisplay() {
    if (this._isShow) {
        if (!this._isFolded) {
            this.$el.hide();
            this._isShow = false;
        } else {
            return this._toggleFold({ isFolded: false });
        }
    } else {
        this.$el.show();
        this._isShow = true;
        this._isFolded = false;
        if (this._isWebRTCSupport) {
            this._$searchInput.focus();
        }
    }
},

async _onToggleDisplay() {
    await this._toggleDisplay();
},

});

return DialingPanel;

});
