package ru.igorlink.minelightsyns;

import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.event.Listener;
import org.bukkit.plugin.java.JavaPlugin;

public class Main extends JavaPlugin implements Listener {
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (sender instanceof Player) {
            return true;
        } else if (args.length > 1) {
            sender.sendMessage("E0");
            return true;
        } else {
            String username = args[0];
            if (this.getServer().getPlayer(username) == null) {
                sender.sendMessage("E1");
                return true;
            } else {
                Player player = this.getServer().getPlayer(username);
                Location player_cords = player.getLocation();
                Location top_block_cords = new Location(player_cords.getWorld(), player_cords.getX(), player_cords.getY() + 1.0D, player_cords.getZ());
                if (top_block_cords != null) {
                    int light_level = top_block_cords.getBlock().getLightLevel();
                    sender.sendMessage(String.valueOf(light_level));
                }

                return true;
            }
        }
    }
}
