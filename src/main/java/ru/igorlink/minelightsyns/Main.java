package ru.igorlink.minelightsyns;

import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.event.Listener;
import org.bukkit.plugin.java.JavaPlugin;


public class Main extends JavaPlugin implements Listener {
    //При вызове нашей команды
    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {

        //Если у команды больше одного аргумента - это ошибка (у нашей команды должен быть один аргумент - ник игрока), возвращаем код E0
        if (args.length > 1) {
            sender.sendMessage("E0");
            return true; //Выходим

        }

        //Если игрок с указанным ником не найден, возвращаем код ошибки E1
        String username = args[0];
        if (getServer().getPlayer(username) == null) {
            sender.sendMessage("E1");
            return true; //Выходим

        }

        Player player = getServer().getPlayer(username); //Получаем объект игрока
        Location player_cords = player.getLocation(); //Получаем координаты игрока
        Location top_block_cords = new Location(player_cords.getWorld(), player_cords.getX(), player_cords.getY() + 1, player_cords.getZ()); //Координаты блока с нашей головой - это на 1 выше, чем координаты игрока
        int light_level = top_block_cords.getBlock().getLightLevel(); //Получаем уровень освещенности блока с головой игрока
        sender.sendMessage(String.valueOf(light_level)); //Отправляем этот уровень освещенности отправителю команды (в нашем проекте это будет программа на питоне, которая будет вызывать команды через rcon)
        

        return true; //Выходим

    }

}
