var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.urlLink = function (props) {
    // Ensure props.value is a string
    if (typeof props.value === 'string' && props.value.startsWith('http')) {
        return React.createElement(
            'a',
            { href: props.value, target: "_blank", rel: "noopener noreferrer" },
            props.value
        );
    } else {
        return props.value;
    }
};
