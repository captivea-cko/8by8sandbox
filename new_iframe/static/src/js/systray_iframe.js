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
        'load': '_onLoad',
    },

    // TODO remove and replace with session_info mechanism
    /**
     * @override
     */
    async willStart() {
        const _super = this._super.bind(this, ...arguments); // limitation of class.js
        return _super();
    },

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClick(ev) {
        ev.preventDefault();
        this.$('.iframe').toggle();
        core.bus.trigger('toggle_iframe');
    },

    /**
     * @private
     * @param {} ev
     */
    _onLoad(ev) {
        alert('Testing if onload event exists');
        console.log(ev);
    },
});

// Insert the Voip widget button in the systray menu
SystrayMenu.Items.push(SystrayIFrameMenu);

return SystrayIFrameMenu;

});
