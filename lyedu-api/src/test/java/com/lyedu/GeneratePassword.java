import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class GeneratePassword {
    public static void main(String[] args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        String password = "lyedu123456";
        String encoded = encoder.encode(password);
        System.out.println("Password: " + password);
        System.out.println("BCrypt Hash: " + encoded);
        System.out.println("Matches: " + encoder.matches(password, encoded));
    }
}
