package ru.igorlink.minelightsyns;

import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.event.Listener;
import org.bukkit.plugin.java.JavaPlugin;


public class Main extends JavaPlugin implements Listener {
    // Коды ошибок, т.к. хардкор нужно выносить в константы
    private static String ERROR_E0 = "E0";
    private static String ERROR_E1 = "E1";

    //При вызове нашей команды
    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args == null || args.length != 1) { // Нужен только один аргумент
            log(ERROR_E0);
            return true;
        }

        //Если игрок с указанным ником не найден, возвращаем код ошибки E1
        String username = args[0];
        if (getServer().getPlayer(username) == null) {
            log(ERROR_E1);
            return true;
        }

        Player player = getServer().getPlayer(username); //Получаем объект игрока
        Location top_block_cords = player.getEyeLocation(); //Получаем координаты головы игрока
        int light_level = top_block_cords.getBlock().getLightLevel(); //Получаем уровень освещенности блока с головой игрока
        sender.sendMessage(String.valueOf(light_level)); //Отправляем этот уровень освещенности отправителю команды (в нашем проекте это будет программа на питоне, которая будет вызывать команды через rcon)
        

        return true; //Выходим

    }

    // Функция для логирования
    private static void log(String message) {
        if (message != null) {
            String messageLog;
            switch (message) {
                case ERROR_E0:
                    messageLog = "Неверные аргументы";
                    break;
                case ERROR_E1:
                    messageLog = "Игрок не найден";
                    break;
                default:
                    messageLog = "Неизвестная ошибка";
                    break;
            }
            System.out.println(messageLog);
            sender.sendMessage(message);
        }
    }
}
