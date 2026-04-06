# Spring Boot Quick Reference

## Setup
- **Maven**: `mvn spring-boot:run`
- **Gradle**: `./gradlew bootRun`

## Common Dependencies (pom.xml)
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

## Running Tests
`mvn test`

## Profiles
- `application-dev.properties` / `application-prod.properties`
- Activate: `spring.profiles.active=dev`

## Useful Annotations
- `@SpringBootApplication`
- `@RestController`, `@RequestMapping`
- `@Autowired`, `@Component`
- `@Transactional`
