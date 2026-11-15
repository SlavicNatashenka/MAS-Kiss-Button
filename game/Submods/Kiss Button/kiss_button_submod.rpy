init -990 python in mas_submod_utils:
    Submod(
        author="Natashenka",
        name="Kiss Button",
        description="Lets you ask Monika for a kiss.",
        version="1.0.0"
    )

init -10 python in hkb_button:
    import store
    import datetime
    
    # Property for enabling the kiss button
    kiss_enabled = True
    
    # Track consecutive kisses for progressive duration
    consecutive_kisses = 0
    last_kiss_time = None
    consecutive_window = datetime.timedelta(minutes=2)  # Reset counter after 2 minutes

init -5 python:
    def KissButtonShow():
        """Shows the kiss button overlay"""
        if "kiss_button_overlay" not in config.overlay_screens:
            config.overlay_screens.append("kiss_button_overlay")
    
    def KissButtonHide():
        """Hides the kiss button overlay"""
        if "kiss_button_overlay" in config.overlay_screens:
            config.overlay_screens.remove("kiss_button_overlay")
            renpy.hide_screen("kiss_button_overlay")
    
    def get_progressive_kiss_duration():
        """Calculate kiss duration based on consecutive kisses"""
        import store.hkb_button as hkb
        
        # Check if we should reset the counter
        if hkb.last_kiss_time is None or not mas_timePastSince(hkb.last_kiss_time, hkb.consecutive_window):
            # Within the time window, increment counter
            hkb.consecutive_kisses += 1
        else:
            # Reset counter if too much time has passed
            hkb.consecutive_kisses = 1
        
        # Update last kiss time
        hkb.last_kiss_time = datetime.datetime.now()
        
        # Progressive duration: starts at 0.5s, increases by 0.5s each time, max 3.0s
        duration = min(0.5 + (hkb.consecutive_kisses - 1) * 0.5, 3.0)
        return duration
    
    # Call this at init time
    KissButtonShow()

# Add the kiss button as a separate overlay - positioned below Extra+ button
screen kiss_button_overlay():
    # Only show when NOT on main menu and when hkb_overlay is visible
    if not main_menu and renpy.get_screen("hkb_overlay"):
        zorder 15
        style_prefix "hkb"

        vbox:
            xpos 0.05
            yanchor 1.0
            ypos 90  # Position below Extra+ button (Extra+ is at 50, so 50 + 40 = 90)

            # Check affection and first kiss status before allowing kiss
            # Disable button during dialogue (when dlg_workflow is True)
            if mas_isMoniEnamored(higher=True) and persistent._mas_first_kiss is not None:
                if not store.mas_globals.dlg_workflow:
                    textbutton _("Kiss") action Jump("mas_kiss_button_wrapper")
                else:
                    textbutton _("Kiss")
            elif mas_isMoniNormal(higher=True):
                if not store.mas_globals.dlg_workflow:
                    textbutton _("Kiss") action Jump("mas_kiss_button_not_ready")
                else:
                    textbutton _("Kiss")
            else:
                if not store.mas_globals.dlg_workflow:
                    textbutton _("Kiss") action Jump("mas_kiss_button_low_aff")
                else:
                    textbutton _("Kiss")

# Enhanced wrapper label with progressive duration and auto-continuation
label mas_kiss_button_wrapper:
    # Check if enough time has passed since last kiss (1 minute cooldown)
    if (
        persistent._mas_last_kiss is not None
        and not mas_timePastSince(persistent._mas_last_kiss, datetime.timedelta(minutes=1))
    ):
        # Rapid consecutive kisses - use enhanced version
        python:
            kiss_quips_again = [
                _("I wouldn't mind another kiss~"),
                _("I'll never get tired of kissing you~"),
                _("I could do that again...{w=0.2}and again...{w=0.7}and again~"),
                _("You can kiss me as many times as you like, [mas_get_player_nickname()]~"),
                _("You know...{w=0.2}you could kiss me again~")
            ]

            kiss_quips_again_risque = [
                _("We can do it the whole day~"),
                _("This almost seems like the start of a make-out session, [player]~"),
                _("I don't think I've had enough just yet, [mas_get_player_nickname()]~"),
                _("That was really nice...{w=0.2}but I want a little more~")
            ]

            # Check if we should use risque dialogue
            use_risque = mas_isMoniLove() and random.randint(1, 10) == 1
            
            if use_risque:
                kiss_quip = renpy.random.choice(kiss_quips_again_risque)
            else:
                kiss_quip = renpy.random.choice(kiss_quips_again)
            
            # Get progressive duration
            kiss_duration = get_progressive_kiss_duration()

        show monika 2tkbsu
        pause 2.0

        call monika_kissing_motion(duration=kiss_duration, initial_exp="6hubsa", final_exp="6tkbfu", fade_duration=0.5)

        show monika 6tkbfu
        $ renpy.say(m, kiss_quip)
        
        # Auto-continue for specific risque lines
        if use_risque and kiss_quip in [
            _("We can do it the whole day~"),
            _("This almost seems like the start of a make-out session, [player]~")
        ]:
            # Monika initiates another kiss
            pause 1.0
            show monika 6dkbsu
            pause 1.5
            
            $ kiss_duration = get_progressive_kiss_duration()
            call monika_kissing_motion(duration=kiss_duration, initial_exp="6dkbsu", final_exp="6ekbfa", fade_duration=0.5)
            
            python:
                kiss_followup = [
                    _("Mmm...{w=0.3}I love you so much, [player]~"),
                    _("That was wonderful, [mas_get_player_nickname()]~"),
                    _("I could kiss you forever, [player]~")
                ]
                followup_quip = renpy.random.choice(kiss_followup)
            
            show monika 6ekbfa
            $ renpy.say(m, followup_quip)
            $ mas_ILY()
    else:
        # First kiss or after cooldown - use standard monika_kiss
        call monika_kiss
    
    jump ch30_loop

# Label for when player hasn't had first kiss yet
label mas_kiss_button_not_ready:
    m 1eka "Aww, [player]..."
    m 1ekbsa "I really appreciate that you want to kiss me..."
    m 3rksdla "But I think we should wait for the right moment."
    m 1ekbfa "When the time comes, it'll be really special~"
    jump ch30_loop

# Label for when affection is too low
label mas_kiss_button_low_aff:
    m 1eka "Aww, [player]..."
    m 3eka "I appreciate the thought, but I think we should get to know each other a bit better first."
    m 1hua "Let's spend more time together, okay?"
    jump ch30_loop