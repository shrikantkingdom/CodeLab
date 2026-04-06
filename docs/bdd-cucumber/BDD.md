# BDD with Cucumber

## Java Setup (Maven)
```xml
<dependency>
    <groupId>io.cucumber</groupId>
    <artifactId>cucumber-java</artifactId>
    <version>7.15.0</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>io.cucumber</groupId>
    <artifactId>cucumber-junit</artifactId>
    <version>7.15.0</version>
    <scope>test</scope>
</dependency>
```

## Feature File Example (`src/test/resources/features/login.feature`)
```gherkin
Feature: Login
  Scenario: Successful login
    Given the user is on the login page
    When they enter valid credentials
    Then they should see the dashboard
```

## Step Definitions
```java
public class LoginSteps {
    @Given("the user is on the login page")
    public void userOnLoginPage() {
        // ...
    }
}
```

## Run with JUnit
```java
@RunWith(Cucumber.class)
@CucumberOptions(features = "src/test/resources/features")
public class RunCucumberTest {}
```
