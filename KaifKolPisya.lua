

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

kaifkol = gui.get_tab("KaifKol menu")

gui.show_message("KaifKolMenu", "Loaded")
AUDIO.PLAY_SOUND_FRONTEND(-1, "MP_AWARD", "HUD_FRONTEND_DEFAULT_SOUNDSET", true)

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Self = kaifkol:add_tab("Self")


Self:add_text("Items")

Self:add_button("Сandies x1000", function()
    stats.set_int("MPx_NO_BOUGHT_YUM_SNACKS", 999)
    stats.set_int("MPx_NO_BOUGHT_HEALTH_SNACKS", 999)
    stats.set_int("MPx_NO_BOUGHT_EPIC_SNACKS", 999)
    stats.set_int("MPx_NUMBER_OF_ORANGE_BOUGH", 999)
end)

Self:add_sameline()

Self:add_button("Body armors х1000", function()
    stats.set_int("MPx_MP_CHAR_ARMOUR_1_COUNT", 999)
    stats.set_int("MPx_MP_CHAR_ARMOUR_2_COUNT", 999)
    stats.set_int("MPx_MP_CHAR_ARMOUR_3_COUNT", 999)
    stats.set_int("MPx_MP_CHAR_ARMOUR_4_COUNT", 999)
    stats.set_int("MPx_MP_CHAR_ARMOUR_5_COUNT", 999)
end)

Self:add_separator()


Stats = Self:add_tab("Stats")

Mental = stats.get_float("MPX_PLAYER_MENTAL_STATE")
Stats:add_imgui(function()
    Mental, used =  ImGui.SliderInt("Mental", Mental, 0, 100)
    if used then
        stats.set_int("MPX_PLAYER_MENTAL_STATE", Mental) 
        stats.set_float("MPX_PLAYER_MENTAL_STATE", Mental)
    end
end)

Stats:add_button("100% Stats", function()
    stats.set_int("MPx_SCRIPT_INCREASE_STAM", 100)
    stats.set_int("MPx_SCRIPT_INCREASE_SHO", 100)
    stats.set_int("MPx_SCRIPT_INCREASE_STRN", 100)
    stats.set_int("MPX_SCRIPT_INCREASE_STL", 100)
    stats.set_int("MPx_SCRIPT_INCREASE_FLY", 100)
    stats.set_int("MPx_SCRIPT_INCREASE_DRIV", 100)  
    stats.set_int("MPx_SCRIPT_INCREASE_LUNG", 100)
end)

Stats:add_sameline()

Stats:add_imgui(function()
    toggle_gender, used = ImGui.Checkbox("Change gender", toggle_gender, true)
    if used then
        if toggle_gender then
            stats.set_int(MPX .. "ALLOW_GENDER_CHANGE", 52)
        else
            tats.set_int(MPX .. "ALLOW_GENDER_CHANGE", 0)
        end
    end
end)

Stats:add_separator()

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Vehicles = kaifkol:add_tab("Cars")

Vehicles:add_button("Remove car sell limit", function()
    stats.set_int("MPPLY_VEHICLE_SELL_TIME", 0)
    stats.set_int("MPPLY_NUM_CARS_SOLD_TODAY", 0)
end)

Vehicles:add_separator()

Vehicles:add_imgui(function()
    toggle_cars, used = ImGui.Checkbox("Back old cars", toggle_cars, true)
    if used then
        local values = {   
            22565, 14708, 34371, 34373, 34451, 34349, 34527, 34533, 17356, 17372, 34589,
            35492, 34415, 34417, 34465, 34573, 34499, 34495, 34493, 34511, 28191, 34501,
            34333, 34551, 34553, 34409, 34365, 34569, 34571, 23726, 34401, 17230, 25367,
            34335, 34337, 34339, 34341, 34325, 18947, 18948, 22564, 17229, 34367, 34331,
            21603, 17364, 25369, 34431, 34453, 34497, 25387, 34455, 34403, 17355, 34399,
            34323, 34437, 23717, 17358, 17370, 34467, 34433, 34435, 34351, 34411, 34587,
            34565, 34523, 34369, 34563, 34559, 34481, 19951, 34581, 34577, 22556, 34585,
            34473, 25386, 22563, 34457, 34513, 22557, 28201, 34405, 34541, 34459, 34535,
            34429, 25383, 34439, 34387, 34361, 34557, 34503, 34583, 28830, 28190, 25379,
            17232, 34353, 34555, 34597, 23729, 14703, 25385, 34471, 25396, 34443, 34441,
            25397, 34591, 34475, 34561, 25389, 34485, 34567, 34427, 34529, 34595, 22560,
            34505, 34355, 34357, 21607, 17363, 17373, 34483, 17223, 34507, 34531, 21606,
            22558, 22562, 34593, 34521, 34377, 34393, 34469, 34489, 19953, 34509, 25393,
            34463, 34461, 17366, 34515, 22561, 22554, 34519, 34345, 34347, 34547, 34579,
            28831, 34445, 34575, 34359, 34479, 23781, 34539, 34383, 34381, 34379, 34545,
            22551, 34343, 34549, 34525, 23780, 34537, 34327, 29156, 20830, 17371, 25370,
            17221, 34407, 34477, 26330, 34375, 29605, 34487, 22566, 34397, 34543, 34517,
            17369, 20828, 34423, 34425, 34395, 34447, 34449, 25384, 17354, 25381, 34599
        }

        for _, value in ipairs(values) do
            globals.set_int(262145 + value, toggle_cars and 1 or 0)
        end
    end
end)

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

World = kaifkol:add_tab("World")

World:add_imgui(function()
    toggle_snow, used = ImGui.Checkbox("Snow", toggle_snow, true)
    if used then
        if toggle_snow then
            gui.show_message("On")
            globals.set_int(262145 + 4413, 1)
        else
            gui.show_message("Off")
            globals.set_int(262145 + 4413, 0)
        end
    end
end)

World:add_separator()

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--[[

* If you have any questions, write to discord: kaifkol

--]]
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------






