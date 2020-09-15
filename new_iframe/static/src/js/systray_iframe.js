odoo.define('iframe_systray', function (require) {
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

const SystrayIFrameMenu = Widget.extend({
    name: 'iframe',
    template: 'show_iframe',
    events: {
        'click': '_onClick',
    },

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClick(ev) {
        ev.preventDefault();
        this.$('.iframe').show();
        core.bus.trigger('toggle_iframe');
    },
});

// Insert the Voip widget button in the systray menu
SystrayMenu.Items.push(SystrayIFrameMenu);

return SystrayIFrameMenu;

});
