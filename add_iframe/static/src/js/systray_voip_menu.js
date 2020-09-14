odoo.define('voip.SystrayVoipMenu', function (require) {
"use strict";

const core = require('web.core');
const config = require('web.config');
const session = require('web.session');
const SystrayMenu = require('web.SystrayMenu');
const Widget = require('web.Widget');

// As voip is not supported on mobile devices,
// we want to keep the standard phone widget
if (config.device.isMobile) {
    return;
}

const SystrayVoipMenu = Widget.extend({
    name: 'voip',
    template: 'voip.switch_panel_top_button',
    events: {
        'click': '_onClick',
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClick(ev) {
        ev.preventDefault();
        core.bus.trigger('voip_onToggleDisplay');
    },
});

// Insert the Voip widget button in the systray menu
SystrayMenu.Items.push(SystrayVoipMenu);

return SystrayVoipMenu;

});
