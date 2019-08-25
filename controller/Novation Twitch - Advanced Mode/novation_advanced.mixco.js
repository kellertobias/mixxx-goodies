// script.twitch
// =============
//
// > This file is part of the [Mixco framework](http://sinusoid.es/mixco).
// > - **View me [on a static web](http://sinusoid.es/mixco/script/novation_twitch.mixco.html)**
// > - **View me [on GitHub](https://github.com/arximboldi/mixco/blob/master/script/novation_twitch.mixco.litcoffee)**
//
// Mixx script file for the **Novation Twitch** controller.
//
// This script serves as **tutorial** for creating scripts using the
// *Mixco* framework, but programming directly in JavaScript.  Still,
// we recommend you to try CoffeeScript, since it is a bit of a nicer
// language.
//
// If you want to modify this script, you may want to read the
// [Novation Twitch Programmer Guide](https://us.novationmusic.com/support/downloads/twitch-programmers-reference-guide)
//
// ### Note for Linux Users
//
// The Linux Kernel version 3.10 is required to get Novation Twitch
// detected as soundcard or MIDI device.
//
//   ![Novation Twitch Layout](http://sinusoid.es/mixco/pic/novation_twitch.png)
//
// Dependencies
// ------------
//
// First, we have to import the modules from the framework.  We use
// that the *NodeJS* `require` function.  Note that all other NodeJS
// modules are usable too when writing your script with the *Mixco*
// framework.
var _ = require('underscore')
var mixco = require('mixco')
var c = mixco.control
var b = mixco.behaviour
var v = mixco.value
var t = mixco.transform

// The script
// ----------
//
// When writing a controller script we use the `script.register`
// function to generate and install a script instance in the current
// module.  The first parameter is the current module as defined by
// *NodeJS*, the second parameter is the JavaScript object with all
// the functions and information about our script.

var CTRL = null;

// Utilities
// ---------
//
// The *scaledDiff* function returns a behaviour option that is useful
// to define encoders with a specific sensitivity, which is useful to
// correct the issues of the stepped encoders.

function scaledDiff(factor) {
    return function(v, v0) {
        return (v0 + factor * (v > 64 ? v - 128 : v)).clamp(0, 128)
    }
}

function scaledSelectKnob(factor) {
    return function(v) {
        return factor * (v > 64 ? v - 128 : v)
    }
}

var redLed   = 0x00
var amberLed = 0x40
var greenLed = 0x70

var loopSizes = [
    "0.125", "0.25", "0.5", "1",
    "2", "4", "8", "16"
]


mixco.script.register(module, {

    // ### Metadata
    //
    // Then the `info` object contains the meta-data that is displayed
    // to the user in the MIDI mapping chooser of Mixxx.

    info: {
        name: "Novation Twitch Advanced Scripted",
        author: "Tobias S. Keller",
        forums: 'https://github.com/arximboldi/mixco/issues',
        wiki: 'https://sinusoid.es/mixco/script/korg_nanokontrol2.mixco.html',
        description: "Controller mapping for Novation Twitch (in advanced mode).",
    },

    // ### Constructor
    //
    // The constructor contains the definition of the MIDI mapping.
    // Here we create all the different control objects and add them
    // to the script instance.

    constructor: function() {
        var pad = function (ids, color) {
            return c.control(ids).states({
                on:  color + 0xf,
                off: color + 0x2
            })
        }

        var self = this

        CTRL = {
            MASTER: {
                CROSSFADE: c.input(0x08, 0x07),
            },
            FX: {
                TOP_LL_ROT:  c.input(c.ccIds(0x5B, 0x7)),
                TOP_ML_ROT:  c.input(0x5C, 0x7),
                TOP_ML_PUSH: c.input(c.noteIds(0x5C, 0x7)),
                TOP_MR_ROT:  c.input(0x5D, 0x7),
                TOP_MR_PUSH: c.input(c.noteIds(0x5D, 0x7)),
                TOP_RR_ROT:  c.input(c.ccIds(0x0C, 0x7)),
                MID_LL: c.control(c.noteIds(0x18, 0x7)),
                MID_ML: c.control(c.noteIds(0x19, 0x7)),
                MID_MR: c.control(c.noteIds(0x1A, 0x7)),
                MID_RR: c.control(c.noteIds(0x0B, 0x7)),
                BOT_LL: c.control(c.noteIds(0x1B, 0x7)),
                BOT_ML: c.control(c.noteIds(0x1C, 0x7)),
                BOT_MR: c.control(c.noteIds(0x1D, 0x7)),
                BOT_RR: c.control(c.noteIds(0x0C, 0x7)),
            },
            BROWSE: {
                ENLARGE: c.control(c.noteIds(0x50, 0x7)),
                PREVIEW: c.control(c.noteIds(0x51, 0x7)),
                PREV: c.input(c.noteIds(0x54, 0x7)),
                NEXT: c.input(c.noteIds(0x56, 0x7)),
                LOAD_1: c.control(c.noteIds(0x52,0x7)),
                LOAD_2: c.control(c.noteIds(0x53,0x7)),
                SCROLL_PUSH: c.input(c.noteIds(0x55, 0x7)),
                SCROLL_ROT: c.input(0x55, 0x7),
            },
            DECK_1: {},
            DECK_2: {},
        }

        for (var i = 0; i < 2; i++) {
            CTRL["DECK_" + (i+1)] = {
                MODE_1: c.control(c.noteIds(0x38, 0x7 + i)),
                MODE_2: c.control(c.noteIds(0x39, 0x7 + i)),
                MODE_3: c.control(c.noteIds(0x3A, 0x7 + i)),
                MODE_4: c.control(c.noteIds(0x3B, 0x7 + i)),
                PAD_1: c.control(c.noteIds(0x3C, 0x7 + i)),
                PAD_2: c.control(c.noteIds(0x3D, 0x7 + i)),
                PAD_3: c.control(c.noteIds(0x3E, 0x7 + i)),
                PAD_4: c.control(c.noteIds(0x3F, 0x7 + i)),
                PAD_5: c.control(c.noteIds(0x40, 0x7 + i)),
                PAD_6: c.control(c.noteIds(0x41, 0x7 + i)),
                PAD_7: c.control(c.noteIds(0x42, 0x7 + i)),
                PAD_8: c.control(c.noteIds(0x43, 0x7 + i)),

                FADE: c.input(c.ccIds(0x07, 0x7 + i)),
                TRIM: c.input(c.ccIds(0x09, 0x7 + i)),
                EQ_H: c.input(c.ccIds(0x48, 0x7 + i)),
                EQ_M: c.input(c.ccIds(0x47, 0x7 + i)),
                EQ_L: c.input(c.ccIds(0x46, 0x7 + i)),

                FX_PUSH: c.control(c.noteIds(0x06, 0x7 + i)),
                FX_ROT: c.input(c.ccIds(0x06, 0x7 + i)),
                FX_PWR: c.control(c.noteIds(0x0D, 0x7 + i)),
                
                PFL: c.control(c.noteIds(0x0A, 0x7 + i)),

                SHIFT: c.control(c.noteIds(0x00, 0x7 + i)),

                CUE: pad(c.noteIds(0x16, 0x7 + i), redLed),
                PLAY: pad(c.noteIds(0x17, 0x7 + i), greenLed),

                BTN_1: c.control(c.noteIds(0x10, 0x7 + i)),
                BTN_2: c.control(c.noteIds(0x11, 0x7 + i)),
                BTN_3: c.control(c.noteIds(0x12, 0x7 + i)),
                BTN_4: c.control(c.noteIds(0x13, 0x7 + i)),

                METER: c.output(c.noteIds(0x5f, 0x7 + i)),

                SWIPE: c.control(c.noteIds(0x14, 0x7 + i)),
                DROP: c.control(c.noteIds(0x15, 0x7 + i)),
                // TOUCH_MODE: c.output(c.ccIds(0x14, 0x7 + i)),
                // TOUCH_STRIP: null,
                // TOUCH_LED: null,
            }
        }

        // t.mappings["waveform_zoom"] = t.linearT(10.0, 1.0)

        t.mappings["AutoDjAddTop"] = t.momentaryT
        t.mappings["AutoDjAddBottom"] = t.momentaryT
        t.mappings["maximize_library"] = t.binaryT
        t.mappings["LoadSelectedTrackAndPlay"] = t.momentaryT
        t.mappings["skip_next"] = t.momentaryT
        t.mappings["fade_now"] = t.momentaryT

        for (var j = 0; j < 8; j++) {
            t.mappings["beatloop_" + loopSizes[j] + "_activate"] = t.momentaryT
            t.mappings["beatloop_" + loopSizes[j] + "_enabled"] = t.momentaryT
            t.mappings["beatloop_" + loopSizes[j] + "_toggle"] = t.momentaryT
            t.mappings["beatlooproll_" + loopSizes[j] + "_activate"] = t.momentaryT
            t.mappings["hotcue_" + (j + 1) + "_activate"] = t.momentaryT
            t.mappings["hotcue_" + (j + 1) + "_enabled"] = t.momentaryT
            t.mappings["cue_preview"] = t.momentaryT
        }


        var shiftEnabled = b.modifier()
        CTRL.DECK_2.SHIFT.does(shiftEnabled)
        CTRL.DECK_1.SHIFT.does("[Recording]", "toggle_recording", "[Recording]", "status")

        // #### Master section
        //
        // Many of the master controls of the that the *headphone
        // volume*, *headphone mix*, *booth volume* and *master volume*
        // knobs are handled directly by the integrated soundcard of
        // the controller.  We map the rest here.

        // // * *Crossfader* slider.
        CTRL.MASTER.CROSSFADE.does("[Master]", "crossfader")

        // CTRL.BROWSE.ENLARGE.does("[Library]", "AutoDjAddBottom")
        // CTRL.BROWSE.PREVIEW.does("[PreviewDeck1]", "LoadSelectedTrackAndPlay")

        CTRL.BROWSE.ENLARGE.when(shiftEnabled, "[Library]", "AutoDjAddTop")
            ._else("[Library]", "AutoDjAddBottom")

        CTRL.BROWSE.PREVIEW.when(shiftEnabled, "[Master]", "maximize_library")
            ._else("[PreviewDeck1]", "LoadSelectedTrackAndPlay")

        CTRL.BROWSE.PREV.does("[Playlist]", "SelectPrevPlaylist")
        CTRL.BROWSE.NEXT.does("[Playlist]", "SelectNextPlaylist")

        CTRL.BROWSE.LOAD_1.does("[Channel1]", "LoadSelectedTrack", "[Channel1]", "end_of_track")
        CTRL.BROWSE.LOAD_2.does("[Channel2]", "LoadSelectedTrack", "[Channel2]", "end_of_track")


        // * The *scroll* encoder scrolls the current view.  When
        //   pressed it moves faster.

        var scrollFaster = b.modifier()

        CTRL.BROWSE.SCROLL_PUSH.does(scrollFaster)
        CTRL.BROWSE.SCROLL_ROT
          .when (scrollFaster,
            b.map("[Playlist]", "SelectTrackKnob")
               .option(scaledSelectKnob(8)))
          .else_(b.map("[Playlist]", "SelectTrackKnob")
               .options.selectknob)
        
        // ### Preview Deck Control
        CTRL.FX.TOP_LL_ROT.does("[PreviewDeck1]", "pregain")
        CTRL.FX.MID_LL.does("[PreviewDeck1]", "play", "[PreviewDeck1]", "beat_active")
        CTRL.FX.BOT_LL.does("[PreviewDeck1]", "cue_preview")

        // ### Display
        CTRL.FX.TOP_RR_ROT.does(b.map("[Channel1]", "waveform_zoom").transform(t.linearT(10,0, 1.0)))
        
        // ### AutoDJ
        CTRL.FX.MID_RR.does("[AutoDJ]", "enabled", "[AutoDJ]", "enabled")
        CTRL.FX.BOT_RR.when(shiftEnabled, "[AutoDJ]", "skip_next")
            ._else("[AutoDJ]", "fade_now")

        // ### FX Controls
        _.map(["ML", "MR"], function(key, i) {
            var fxChain = "EffectRack1_EffectUnit" + (i + 1) + ""
            var fxShift = b.modifier()
            CTRL.FX["TOP_" + key + "_PUSH"].does(fxShift)

            // @TODO: Find out correct transformation function
            CTRL.FX["TOP_" + key + "_ROT"].option(scaledDiff(1 / 2))
                .when (fxShift,
                    b.map("[" + fxChain + "]", "mix").transform(t.linearT(0.0,10.0))
                )
                .else_(
                    b.map("[" + fxChain + "_Effect1]", "meta").transform(t.linearT(0.0,10.0))
                )
        })
        _.map(["MID", "BOT"], function(key, i) {
            CTRL.FX[key + '_ML']
                .does("[EffectRack1_EffectUnit" + (i + 1) + "]", "group_[Channel1]_enable")
            CTRL.FX[key + '_MR']
                .does("[EffectRack1_EffectUnit" + (i + 1) + "]", "group_[Channel2]_enable")
        })

        // ### Per deck controls
        this.decks = b.chooser()
        this.addDeck(0)
        this.addDeck(1)

    },

    addDeck: function(i) {
        var self = this
        var g = "[Channel" + (i + 1) + "]"
        var DECK = CTRL['DECK_' + (i + 1)];
        // #### Mixer section
        //
        DECK.PFL.does(this.decks.add(g, "pfl"))

        DECK.BTN_1.does(g, "quantize")
        DECK.BTN_2.does(g, "keylock")
        // DECK.BTN_2.does(g, "sync_enabled")
        DECK.BTN_3.does(g, "bpm_tap", g, "beat_active")
        DECK.BTN_4.does(g, 'beats_translate_curpos')

        DECK.FADE.does(g, "volume")
        DECK.EQ_L.does(g, "filterLow")
        DECK.EQ_M.does(g, "filterMid")
        DECK.EQ_H.does(g, "filterHigh")
        DECK.TRIM.does(g, "pregain")

        DECK.METER.does(b.mapOut(g, "VuMeter").meter())

        // * The **fader FX** we use to control the quick filter.  The
        //   **on/off** button below can be used to toggle it.
        //   Likewise, pressing the knob momentarily toggles it.
        DECK.FX_ROT.option(scaledDiff(1 / 2)).does("[QuickEffectRack1_" + g + "]", 'super1')
        DECK.FX_PUSH.does("[QuickEffectRack1_" + g + "]", 'enabled')
        DECK.FX_PWR.does("[QuickEffectRack1_" + g + "]", 'enabled')


        DECK.PLAY.does(g, "play")
        DECK.CUE.does(g, "cue_default", g, "cue_indicator")
        
        // slipMode = b.switch_()
        // LEFT BTN: Scratch
        // RIGHT BTN: Search
        // SHOW REMAINING TIME ON TOUCHSTRIP + BLINKING
        // EXAMPLE: c.control(noteIdShift(0x12)).does(slipMode)

        // padTab = b.chooser()
        // DECK.MODE_LL.does(padTab.add())
        // DECK.MODE_ML.does(padTab.add())
        // DECK.MODE_MR.does(padTab.add())
        // DECK.MODE_RR.does(padTab.add())


        // ===================================================
        // #### Pitch
        //
        // * The *pitch* encoder moves the pitch slider up and
        //   down. When it is pressed, it moves it pitch faster.
        var coarseRateFactor = 1/10
        var coarseRateOn     = b.modifier()

        c.input(c.noteIds(0x03, 0x7 + i)).does(coarseRateOn)
        c.input(c.ccIds(0x03, 0x7 + i))
          .when (coarseRateOn,
           b.map(g, "rate").option(scaledDiff(2)))
          .else_(b.map(g, "rate").option(scaledDiff(1/12)))

        // ===================================================
        // #### Transport Bar and Optical Feedback
        // DECK.DROP.does(g, "outro_end_activate", g, "outro_end_enabled")

        // orientation (Crossfade Pos: 0-1-2)
        // perhaps control with value.value (https://sinusoid.es/mixco/src/value.html)
        // playposition
        c.control(c.noteIds(0x16, 0xb7 + i)).does(b.playhead(g))
        // * In *drop* mode, the touch strip scrolls through the song.
        var isSearchMode = false
        DECK.SWIPE.does(b.call(function(ev) {
            print ("Hallo")
            // sendSysexMsg
            if(ev.value > 0) {
                if(!isSearchMode) {
                    // Setup Strip
                    self.mixxx.midi.sendShortMsg(0xb7 + i, 0x14, 0x02)

                    // Visual Feedback
                    DECK.SWIPE.send("on")
                    isSearchMode = true
                } else {
                    // Setup Strip
                    self.mixxx.midi.sendShortMsg(0xb7 + i, 0x14, 0x10)

                    // Visual Feedback
                    DECK.SWIPE.send("off")
                    isSearchMode = false
                }
            }
        }))
        c.input(c.ccIds(0x34, 0x7+i)).does(g, "playposition")

        // * In *swipe* mode, the touch strip nudges the pitch up and
        //   down.  When *shift* is held it simulates scratching.
        // this.mixxx.midi.sendShortMsg(0xb7, 0x14, 0x10)
        c.input(c.ccIds(0x35, 0x7+i))
            .does(b.scratchTick(i + 1))
            .options.selectknob,
        c.input(c.noteIds(0x47, 0x7+i))
            .does(b.scratchEnable(i + 1, 128))


        // ===================================================
        // #### Performance modes
        var currentPerformanceMode = 0
        var performanceMode = []
        var performanceModeValues = []
        _.map([1,2,3,4], function(j) {
            var CURRENT_CONTROL = DECK['MODE_' + (j)]
            performanceModeValues[j - 1] = v.value(0)
            // performanceMode[j - 1]  = b.when(performanceModeValues[j - 1])

            CURRENT_CONTROL.does(b.call(function(ev) {
                if(!(ev.value > 0)) return
                if(currentPerformanceMode != j) {
                    currentPerformanceMode = j
                    // Visual Feedback
                    for(var jj = 0; jj < 4; jj ++) {
                        if(jj == j - 1) continue
                        DECK['MODE_' + (jj + 1)].send("off")
                        performanceModeValues[jj].setValue(0)
                    }
                    CURRENT_CONTROL.send("on")
                    performanceModeValues[j-1].setValue(1)
                }
            }))
        })

        performanceModeValues[0].setValue(0)
        // DECK['MODE_1'].send("on")

        for (var j = 0; j < 8; j++) {
            DECK['PAD_' + (j + 1)].when(
                performanceModeValues[0],
                g, "hotcue_" + (j + 1) + "_activate",
                g, "hotcue_" + (j + 1) + "_enabled"
            )
        }

        for (var j = 0; j < 8; j++) {
            DECK['PAD_' + (j + 1)].when(
                performanceModeValues[2],
                g, "beatloop_" + loopSizes[j] + "_toggle",
                g, "beatloop_" + loopSizes[j] + "_enabled"
            )
        }

        for (var j = 0; j < 8; j++) {
            DECK['PAD_' + (j + 1)].when(
                performanceModeValues[3],
                g, "beatlooproll_" + loopSizes[j] + "_activate",
                g, "beatloop_" + loopSizes[j] + "_enabled"
            )
        }

        for (var j = 0; j < 4; j++) {
            DECK['PAD_' + (j + 1)].when(
                performanceModeValues[1],
                '[Sampler' + (i * 2 + j + 1) + ']', "cue_preview"
            )
        }

        DECK['PAD_5'].when(performanceModeValues[1], b.spinback(i + 1))
        DECK['PAD_6'].when(performanceModeValues[1], b.brake(i + 1))
        DECK['PAD_7'].when(performanceModeValues[1], b.stutter(g, 1 / 8))
        DECK['PAD_8'].when(performanceModeValues[1], b.stutter(g, 1 / 4))
    },

    // ### Initialization
    //
    // The `preinit` function is called before the MIDI controls are
    // initialized.  We are going to set the device in *advanced mode*,
    // as mentioned in the manual. This means that mode management is
    // done by the device -- this will simplify the script and let
    // have direct lower latency mappings more often.

    preinit: function() {
        // this.mixxx.midi.sendShortMsg(0xb7, 0x00, 0x6f)
        // this.mixxx.midi.sendShortMsg(0xb7, 0x00, 0x00)
        this.mixxx.midi.sendShortMsg(0xb7, 0x00, 0x6f)
        this.mixxx.midi.sendShortMsg(0xb7, 0x14, 0x10)
        this.mixxx.midi.sendShortMsg(0xb8, 0x14, 0x10)
    },

    init: function() {
        this.decks.activate(0)
    },

    // ### Shutdown
    //
    // The documentation suggests to reset the device when the program
    // shuts down. This means that all the lights are turned off and
    // the device is in basic mode, ready to be used by some other
    // program.

    postshutdown: function() {
        this.mixxx.midi.sendShortMsg(0xb7, 0x00, 0x00)
    }

});
