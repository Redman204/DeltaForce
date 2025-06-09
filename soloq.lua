local SOLO_MISSIONS <const> = gui.add_tab("Solo Missions")
     
    local FMMC_LAUNCHER <const> = "fmmc_launcher"
    local FM_MISSION_CONTROLLER <const> = "fm_mission_controller"
    local FM_MISSION_CONTROLLER_2020 <const> = "fm_mission_controller_2020"
     
    local function SET_BIT(value, position)
        return (value | (1 << position))
    end
     
    local SoloMissions = SOLO_MISSIONS:add_checkbox("Solo Missions")
     
    SOLO_MISSIONS:add_button("Skip to Next Checkpoint", function() --Credits to Rostal
        if script.is_active(FM_MISSION_CONTROLLER) then
            local value = locals.get_int(FM_MISSION_CONTROLLER, 19781 + 2) 
            value = SET_BIT(value, 17)
            locals.set_int(FM_MISSION_CONTROLLER, 19781 + 2, value)
        elseif script.is_active(FM_MISSION_CONTROLLER_2020) then
            local value = locals.get_int(FM_MISSION_CONTROLLER_2020, 52171 + 2) 
            value = SET_BIT(value, 17)
            locals.set_int(FM_MISSION_CONTROLLER_2020, 52171 + 2, value) 
        end
    end)
     
    SOLO_MISSIONS:add_button("Mission Passed", function()
        for i = 0, 5 do
             globals.set_string(4718592 + 128791 + 1 + i * 6, "")      
        end
     
        if script.is_active(FM_MISSION_CONTROLLER) then
            locals.set_int(FM_MISSION_CONTROLLER, 19781 + 1062, 5) 
            locals.set_int(FM_MISSION_CONTROLLER, 19781 + 1232 + 1, 999999) 
     
            local value = locals.get_int(FM_MISSION_CONTROLLER, 19781 + 1)
            value = SET_BIT(value, 9)
            value = SET_BIT(value, 16)
            locals.set_int(FM_MISSION_CONTROLLER, 19781 + 1, value)
        elseif script.is_active(FM_MISSION_CONTROLLER_2020) then
            locals.set_int(FM_MISSION_CONTROLLER_2020, 52171 + 1589, 5) 
            locals.set_int(FM_MISSION_CONTROLLER_2020, 52171 + 1776 + 1, 999999) 
     
            local value = locals.get_int(FM_MISSION_CONTROLLER_2020, 52171 + 1)
            value = SET_BIT(value, 9)
            value = SET_BIT(value, 16)
            locals.set_int(FM_MISSION_CONTROLLER_2020, 52171 + 1, value)
        end
    end)
     
    SOLO_MISSIONS:add_sameline()
     
    SOLO_MISSIONS:add_button("Mission Failed", function()
        if script.is_active(FM_MISSION_CONTROLLER) then
            local value = locals.get_int(FM_MISSION_CONTROLLER, 19781 + 1)
            value = SET_BIT(value, 16)
            value = SET_BIT(value, 20)
            locals.set_int(FM_MISSION_CONTROLLER, 19781 + 1, value)
        elseif script.is_active(FM_MISSION_CONTROLLER_2020) then
            local value = locals.get_int(FM_MISSION_CONTROLLER_2020, 52171 + 1)
            value = SET_BIT(value, 16)
            value = SET_BIT(value, 20)
            locals.set_int(FM_MISSION_CONTROLLER_2020, 52171 + 1, value)
        end
    end)
     
    script.register_looped("SOLO_MISSIONS", function()
        if SoloMissions:is_enabled() then
            if script.is_active(FMMC_LAUNCHER) then
                local iArrayPos = locals.get_int(FMMC_LAUNCHER, 19875 + 34) 
                if iArrayPos > 0 then
                    locals.set_int(FMMC_LAUNCHER, 19875 + 15, 1) 
                    globals.set_int(794744 + 4 + 1 + iArrayPos * 89 + 69, 1) 
                end
            end
            globals.set_int(4718592 + 3523, 1) 
            globals.set_int(4718592 + 3529 + 1, 1) 
            globals.set_int(4718592 + 180865 + 1, 0)
            globals.set_int(4718592 + 3526, 1)
            globals.set_int(4718592 + 3527, 1)
        end
    end)