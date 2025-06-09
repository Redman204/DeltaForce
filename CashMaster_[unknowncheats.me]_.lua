-- Example of a menu to choose the character's account balance in GTA Online

gui.show_message("FSL Menu", "Choose the value for your account!")

local FSL = {}
FSL.__index = FSL

function FSL.new()
    local instance = setmetatable({}, FSL)
    return instance
end

-- Function to set the account balance
function FSL:SetAccountBalance(value)
    -- Using FSL DLL to modify the player's bank balance
    STATS.STAT_SET_INT(joaat("MP0_WALLET_BALANCE"), value, true)
    gui.show_message("Success", "Your balance has been updated!")
end

-- Function to create the money value menu
function FSL:CreateMenu()
    local tab = gui.get_tab("FSL Menu")
    local subTab = tab:add_tab("Change Balance")

    -- Adding value options
    subTab:add_button("Add 1M", function() 
        self:SetAccountBalance(1000000)  -- Setting balance to 1M
    end)

    subTab:add_button("Add 5M", function()
        self:SetAccountBalance(5000000)  -- Setting balance to 5M
    end)

    subTab:add_button("Add 10M", function()
        self:SetAccountBalance(10000000)  -- Setting balance to 10M
    end)

    subTab:add_button("Add 50M", function()
        self:SetAccountBalance(50000000)  -- Setting balance to 50M
    end)
    subTab:add_button("GREED! 1B", function()
        self:SetAccountBalance(1000000000)  -- Setting balance to 1B
    end)
end

-- Initializing the menu
FSL.new():CreateMenu()
