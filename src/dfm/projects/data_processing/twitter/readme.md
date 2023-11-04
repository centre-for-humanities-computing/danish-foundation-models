For the tweets we process each of them into their individual conversation id and then recursively resolve them into conversations on the form:

```
User 1: {text}
    User 2: {response to 1}
        User 3: {response to 1 and 2}
        taler 1: {response to 2}
    taler 4: {response to 1}
```